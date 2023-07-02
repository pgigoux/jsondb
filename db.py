import os
import re
import json
from os.path import exists
from items import ItemCollection, FieldCollection, Item, Field
from common import KEY_NAME, KEY_UID
from common import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_SENSITIVE_KEY
from common import ITEM_NAME_KEY, ITEM_TAG_LIST_KEY, ITEM_NOTE_KEY, ITEM_TIMESTAMP_KEY, ITEM_FIELDS_KEY
from common import DEFAULT_DATABASE_NAME
from tables import TagTable, FieldTable
from utils import timestamp
from crypt import Crypt

# The database is stored on disk as a json dictionary with three keys
DB_TAGS_KEY = 'tags'
DB_FIELDS_KEY = 'fields'
DB_ITEMS_KEY = 'items'

# Temporary file used when saving data
TEMP_FILE = 'db.tmp'


class Database:

    def __init__(self, file_name, password=''):
        """
        :param file_name: database file name
        :param password: password for data encryption (optional)
        """
        self.file_name = file_name
        self.tag_table = TagTable()
        self.field_table = FieldTable()
        self.item_collection = ItemCollection()
        # The database will be encrypted if a password is supplied
        # self.encrypt_flag = True if password else False
        # self.crypt_key = Crypt(password) if self.encrypt_flag else None
        self.crypt_key = Crypt(password) if password else None

    def read_mode(self) -> str:
        """
        Return the file write mode depending on whether encryption is enabled
        :return: write mode
        """
        # return 'rb' if self.encrypt_flag else 'r'
        return 'r' if self.crypt_key is None else 'rb'

    def write_mode(self) -> str:
        """
        Return the file write mode depending on whether encryption is enabled
        :return: write mode
        """
        # return 'wb' if self.encrypt_flag else 'w'
        return 'w' if self.crypt_key is None else 'wb'

    def read(self):
        """
        Read the database file from disk
        """
        with open(self.file_name, self.read_mode()) as f_in:
            data = f_in.read()
            if self.crypt_key is not None:
                assert isinstance(data, bytes)
                data = self.crypt_key.decrypt_byte2str(data)
            json_data = json.loads(data)

            # Read the tag table
            for tag in json_data[DB_TAGS_KEY]:
                self.tag_table.add(tag[KEY_NAME], tag[KEY_UID])

            # Read the field table
            for field in json_data[DB_FIELDS_KEY]:
                self.field_table.add(field[FIELD_NAME_KEY], field[FIELD_SENSITIVE_KEY])

            # Read the items
            for item_uid in json_data[DB_ITEMS_KEY]:
                item = json_data[DB_ITEMS_KEY][item_uid]
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
        """
        # Convert the database into json and encrypt if an encryption key is defined
        json_data = json.dumps(self.export())
        # data = self.crypt_key.encrypt_s2b(json_data) if self.encrypt_flag else json_data
        data = json_data if self.crypt_key is None else self.crypt_key.encrypt_str2byte(json_data)

        # Write the data to a temporary file first
        with open(TEMP_FILE, self.write_mode()) as f_out:
            f_out.write(data)
        f_out.close()

        # Rename files. The old file is renamed using a time stamp.
        if exists(self.file_name):
            os.rename(self.file_name, self.file_name + '-' + timestamp())
        os.rename(TEMP_FILE, self.file_name)

    def import_from_json(self, encrypt_sensitive=True):
        """
        :param encrypt_sensitive:
        :return:
        """
        pass

    def export_to_json(self, decrypt_sensitive=True):
        """
        Export the database as json
        :param decrypt_sensitive: write sensitive data in plain text?
        :return:
        """
        d = self.export()
        print(d.keys())
        pass

    def search(self, pattern: str, item_name=False, field_name=False, field_value=False,
               tag=False, note=False) -> list[Item]:
        """
        :param pattern: pattern to search for
        :param item_name: search in item name?
        :param field_name: search in field name?
        :param field_value: search in field value?
        :param tag: search in tags?
        :param note: search in note?
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

    def export(self):
        """
        Export the database as a dictionary
        :return:
        """
        return {DB_TAGS_KEY: self.tag_table.export(),
                DB_FIELDS_KEY: self.field_table.export(),
                DB_ITEMS_KEY: self.item_collection.export()}

    def dump(self):
        print(f'-- Database {self.file_name}')
        self.tag_table.dump()
        self.field_table.dump()
        self.item_collection.dump()


if __name__ == '__main__':
    db = Database(DEFAULT_DATABASE_NAME, 'test')
    db.read()
    # db.dump()
    db.export_to_json()
    pass
