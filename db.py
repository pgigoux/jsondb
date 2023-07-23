import os
import re
import json
from typing import Optional
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
        self.crypt_key = Crypt(password) if password else None

    def read_mode(self) -> str:
        """
        Return the file write mode depending on whether encryption is enabled
        :return: write mode
        """
        return 'r' if self.crypt_key is None else 'rb'

    def write_mode(self) -> str:
        """
        Return the file write mode depending on whether encryption is enabled
        :return: write mode
        """
        return 'w' if self.crypt_key is None else 'wb'

    def clear(self):
        """
        Clear data. This function will be used to initialize the database to avoid leaving it
        in an undefined state (e.g. if a read fails half the way through).
        """
        self.tag_table = TagTable()
        self.field_table = FieldTable()
        self.item_collection = ItemCollection()

    def read(self):
        """
        Read the database file from disk
        :raise FileNotFoundError, ValueError
        """
        with open(self.file_name, self.read_mode()) as f_in:
            data = f_in.read()
            if self.crypt_key is not None:
                assert isinstance(data, bytes)
                try:
                    data = self.crypt_key.decrypt_byte2str(data)
                except Exception as e:
                    raise ValueError(f'failed to decrypt data: {repr(e)}')
            try:
                json_data = json.loads(data)
            except Exception as e:
                raise ValueError(f'failed to read the data: {repr(e)}')

            # Read the tag table
            try:
                for tag in json_data[DB_TAGS_KEY]:
                    self.tag_table.add(tag[KEY_NAME], tag[KEY_UID])
            except Exception as e:
                self.clear()
                raise ValueError(f'failed to read tag table: {repr(e)}')

            # Read the field table
            try:
                for field in json_data[DB_FIELDS_KEY]:
                    self.field_table.add(field[FIELD_NAME_KEY], field[FIELD_SENSITIVE_KEY])
            except Exception as e:
                self.clear()
                raise ValueError(f'failed to read field table: {repr(e)}')

            # Read the items
            try:
                for item_uid in json_data[DB_ITEMS_KEY]:
                    item = json_data[DB_ITEMS_KEY][item_uid]
                    fc = FieldCollection()
                    for field_uid in item[ITEM_FIELDS_KEY]:
                        field = item[ITEM_FIELDS_KEY][field_uid]
                        fc.add(Field(field[FIELD_NAME_KEY], field[FIELD_VALUE_KEY], field[FIELD_SENSITIVE_KEY]))
                    self.item_collection.add(Item(item[ITEM_NAME_KEY], item[ITEM_TAG_LIST_KEY],
                                                  item[ITEM_NOTE_KEY], item[ITEM_TIMESTAMP_KEY], fc))
            except Exception as e:
                self.clear()
                raise ValueError(f'failed to read items: {repr(e)}')

        f_in.close()

    def write(self):
        """
        Write the database file to disk
        """
        # Convert the database into json and encrypt if an encryption key is defined
        json_data = json.dumps(self.export())
        data = json_data if self.crypt_key is None else self.crypt_key.encrypt_str2byte(json_data)

        # Write the data to a temporary file first
        with open(TEMP_FILE, self.write_mode()) as f_out:
            f_out.write(data)
        f_out.close()

        # Rename files. The old file is renamed using a time stamp.
        if exists(self.file_name):
            os.rename(self.file_name, self.file_name + '-' + timestamp())
        os.rename(TEMP_FILE, self.file_name)

    def export_to_json(self, file_name: str):
        """
        Export the database as json into a file
        """
        d = self.export(crypt=self.crypt_key)
        json_data = json.dumps(d)
        with open(file_name, 'w') as f:
            f.write(json_data)
            f.close()

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

    def export(self, crypt: Optional[Crypt] = None):
        """
        Export the database as a dictionary
        :return:
        """
        return {DB_TAGS_KEY: self.tag_table.export(),
                DB_FIELDS_KEY: self.field_table.export(),
                DB_ITEMS_KEY: self.item_collection.export(crypt=crypt)}

    def dump(self):
        print(f'-- Database {self.file_name}')
        self.tag_table.dump()
        self.field_table.dump()
        self.item_collection.dump()


if __name__ == '__main__':
    db = Database(DEFAULT_DATABASE_NAME, 'test')
    db.read()
    db.dump()
    # db.export_to_json('export.json')
