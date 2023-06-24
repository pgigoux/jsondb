import os
import re
import json
from os.path import exists
from items import ItemCollection, FieldCollection, Item, Field
from common import KEY_NAME, KEY_UID
from common import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_SENSITIVE_KEY
from common import ITEM_NAME_KEY, ITEM_TAG_LIST_KEY, ITEM_NOTE_KEY, ITEM_TIMESTAMP_KEY, ITEM_FIELDS_KEY
from tables import TagTable, FieldTable
from utils import timestamp
from crypt import Crypt

# The database is stored on disk as a json dictionary with three keys
DB_TAGS_KEY = 'tags'
DB_FIELDS_KEY = 'fields'
DB_ITEMS_KEY = 'items'

# Database name
DATABASE_NAME = 'pw.db'

# Temporary file used when saving data
TEMP_FILE = 'db.tmp'


class Database:

    def __init__(self, file_name, password: str):
        self.file_name = file_name
        self.tag_table = TagTable()
        self.field_table = FieldTable()
        self.item_collection = ItemCollection()
        self.crypt = Crypt(password)

    def add_item(self, item: Item):
        """
        Add an item to the database
        :param item:
        """
        self.item_collection.add(item)

    def remove_item(self, uid: str):
        """
        Remove item from the database
        :param uid: unique identifier
        """
        self.item_collection.remove(uid)

    def read(self):
        """
        Read the database file from disk
        raise: FileNotFoundError
        """
        with open(self.file_name, 'r') as f_in:
            # Read the data form the file
            data = json.loads(f_in.read())

            # Read the tag table
            for tag in data[DB_TAGS_KEY]:
                self.tag_table.add(tag[KEY_NAME], tag[KEY_UID])

            # Read the field table
            for field in data[DB_FIELDS_KEY]:
                self.field_table.add(field[FIELD_NAME_KEY], field[FIELD_SENSITIVE_KEY])

            # Read the items
            for item_uid in data[DB_ITEMS_KEY]:
                item = data[DB_ITEMS_KEY][item_uid]
                fc = FieldCollection()
                for field_uid in item[ITEM_FIELDS_KEY]:
                    field = item[ITEM_FIELDS_KEY][field_uid]
                    fc.add(Field(field[FIELD_NAME_KEY], field[FIELD_VALUE_KEY], field[FIELD_SENSITIVE_KEY]))
                self.item_collection.add(Item(item[ITEM_NAME_KEY], item[ITEM_TAG_LIST_KEY],
                                              item[ITEM_NOTE_KEY], item[ITEM_TIMESTAMP_KEY], fc))

        f_in.close()

    def write(self):
        """
        Write the database file to disk
        :return:
        """
        # Construct the database into a single dictionary
        d = {DB_TAGS_KEY: self.tag_table.to_dict(),
             DB_FIELDS_KEY: self.field_table.to_dict(),
             DB_ITEMS_KEY: self.item_collection.to_dict()}

        # Write the data to a temporary file
        with open(TEMP_FILE, 'w') as f_out:
            json.dump(d, f_out)
        f_out.close()

        # Rename files. The old file is renamed using a time stamp.
        if exists(self.file_name):
            os.rename(self.file_name, self.file_name + '-' + timestamp())
        os.rename(TEMP_FILE, self.file_name)

    def export(self):
        pass

    def search(self, pattern: str, item_name=False, field_name=False, field_value=False,
               tag=False, note=False) -> list[Item]:
        """
        :param pattern: pattern to search for
        :param item_name: search in item name?
        :param field_name: search in field name?
        :param field_value: search in field value?
        :param tag: search in tags?
        :param note: seach in note?
        :return: list of items matching the search criteria
        """
        output_list = []
        cp = re.compile(pattern, flags=re.IGNORECASE)
        for item in self.item_collection.next():
            assert isinstance(item, Item)
            if item_name and cp.search(item.name):
                output_list.append(item)
            if field_name or field_value:
                for field in item.next_field():
                    if field_name and cp.search(field.name):
                        output_list.append(item)
                    if field_value and cp.search(field.value):
                        output_list.append(item)
            if tag and pattern in item.tags:
                output_list.append(item)
            if note and cp.search(item.note):
                output_list.append(item)

        return output_list

    def dump(self):
        print(f'-- Database {self.file_name}')
        self.tag_table.dump()
        self.field_table.dump()
        self.item_collection.dump()


if __name__ == '__main__':
    db = Database('db.json', 'test_password')
    db.read()
    db.dump()
