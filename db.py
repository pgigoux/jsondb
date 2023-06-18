import os
from os.path import exists
from items import ItemCollection, FieldCollection, Item, Field
from items import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_SENSITIVE_KEY
from items import ITEM_NAME_KEY, ITEM_TAG_LIST_KEY, ITEM_NOTE_KEY, ITEM_TIMESTAMP_KEY, ITEM_FIELDS_KEY
from common import KEY_NAME, KEY_UID
from tables import TagTable, FieldTable
from utils import match_strings, timestamp
import json

# The database is stored on disk as a json dictionary with three keys
DB_TAGS_KEY = 'tags'
DB_FIELDS_KEY = 'fields'
DB_ITEMS_KEY = 'items'

# Database name
DATABASE_NAME = 'pw.db'

# Temporary file used when saving data
TEMP_FILE = 'db.tmp'


class Database:

    def __init__(self, file_name):
        self.file_name = file_name
        self.tag_table = TagTable()
        self.field_table = FieldTable()
        self.item_collection = ItemCollection()

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
        :return:
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

    def search(self, item_name='', field_name='', field_value='', tag='') -> list[Item]:
        output_list = []
        for item in self.item_collection.next():
            assert isinstance(item, Item)
            if item_name and match_strings(item_name, item.name):
                output_list.append(item)
            if field_name:
                for field in item.next_field():
                    if match_strings(field_name, field.name):
                        output_list.append(item)
            if field_value:
                for field in item.next_field():
                    if match_strings(field_value, field.value):
                        output_list.append(item)
            if tag:
                # TODO
                pass
        return output_list

    def dump(self):
        print('---- Database ----')
        print(f'file_name={self.file_name}')
        self.tag_table.dump()
        self.field_table.dump()
        self.item_collection.dump()


if __name__ == '__main__':
    db = Database('db.json')
    db.read()
    for it in db.search(item_name='fala', field_name='RUT', field_value='rtimp'):
        it.dump()
    # db.dump()
