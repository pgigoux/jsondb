#!/usr/bin/env python
"""
Program used to import a password database exported from Enpass in json format
It generates an output database with much less information.

The input file is dictionary containing two lists: folders and items. Each folder is in turn a dictionary
of string values. Each item is a dictionary containing numbers, strings, lists of strings and list of
subdictionaries. Only a few elements in the items are really relevant.

{
    "folders": [
        {
            "icon": "1008",
            "parent_uuid": "",
            "title": "Business",
            "updated_at": 1527696441,
            "uuid": "f7a59f9c-c7c5-409f-8e3b-3ce4ea57519a"
        },
        ... more folders
    ]
    "items": [
        {
            "archived": 0,
            "auto_submit": 1,
            "category": "misc",
            "createdAt": 1527696211,
            "favorite": 0,
            "fields": [
                {
                    "deleted": 0,
                    "label": "Access number",
                    "order": 1,
                    "sensitive": 0,
                    "type": "numeric",
                    "uid": 0,
                    "updated_at": 1527696211,
                    "value": "",
                    "value_updated_at": 1527696211
                },
                {
                    "deleted": 0,
                    "label": "PIN",
                    "order": 2,
                    "sensitive": 1,
                    "type": "pin",
                    "uid": 1,
                    "updated_at": 1527696211,
                    "value": "0000",
                    "value_updated_at": 1527696211
                }
            ],
            "folders": [
                "f7a59f9c-c7c5-409f-8e3b-3ce4ea57519a"
            ],
            "icon": {
                "fav": "",
                "image": {
                    "file": "misc/calling"
                },
                "type": 1,
                "uuid": ""
            },
            "note": "",
            "subtitle": "",
            "template_type": "misc.voicemail",
            "title": "LATAM",
            "trashed": 0,
            "updated_at": 1527696294,
            "uuid": "2d4dc0e9-b0df-4197-9c93-cbf422688520"
        },
        ... more items
    ]
}
"""
import json
import argparse
import sys

from db import Database
from crypt import Crypt
from uid import TagTableUid
from items import FieldCollection, Item, Field
from utils import trimmed_string, get_password
from common import DEFAULT_DATABASE_NAME

# Files used to save tables into separate files
FIELD_FILE_NAME = 'fields.csv'
TAG_FILE_NAME = 'tags.csv'

# Default tag for those items that do not have one
TAG_DEFAULT = 'default'

# Dictionary used to map the tag identifiers in the input file to new ids
# The dictionary will be indexed by the tag uid from the file
# Each entry in the dictionary will be a tuple containing the tag name and the new uid
tag_dict = {}


def process_field(field: dict) -> tuple:
    """
    Process field contents.
    Ignore fields that have no value or that are of no interest
    Rename some fields and make sure the sensitive flag is set for specific fields
    :param field: field contents
    :return: field name, value and sensitive flag
    :raise: ValueError if the field contents is empty or of no interest
    """
    # Extract the field name, value and sensitive flag
    f_name = trimmed_string(field['label'])
    f_sensitive = True if field['sensitive'] == 1 else False
    f_value = trimmed_string(field['value'])

    # Ignore fields with certain names or empty values
    if not f_value:
        raise ValueError(f'empty field {f_name}')
    if f_name in ['508', 'If lost, call']:
        raise ValueError(f'ignored name {f_name}')

    # Fix naming problems and sensitive flags
    if f_name == 'Add. password':
        f_name = 'Additional password'
    elif f_name == 'Handset Model':
        f_name = 'Model'
    elif f_name == 'Username':
        f_name = "User name"
    elif f_name in ['Consumer ID', 'Consumer Id', 'Customer id']:
        f_name = 'Customer Id'
    elif f_name == 'Host Name':
        f_name = 'Host name'
    elif f_name == 'E-mail':
        f_name = 'Email'
    elif f_name in ['Expiry date', 'Expiration date', 'Valid']:
        f_name = 'Valid until'
    elif f_name == 'MAC/Airport #':
        f_name = 'MAC'
    elif f_name == 'Server/IP address':
        f_name = 'IP address'
    elif f_name == 'Website':
        f_name = 'URL'
    elif f_name == 'Serial':
        f_name = 'Serial number'
    elif f_name == 'Login name':
        f_name = 'Login'
    elif f_name == 'ID number':
        f_name = 'ID'
    elif 'Security Answer' in f_name:
        f_name = f_name.replace('Security Answer', 'Security answer')
    elif 'Securiry' in f_name:
        f_name = f_name.replace('Securiry', 'Security')
    elif 'Security answer' in f_name:
        f_sensitive = True

    f_name = f_name.replace(' ', '_')

    return f_name.lower(), f_value, f_sensitive


def process_tag(name: str, uid: str) -> tuple[str, str]:
    """
    Rename some tags
    :param name: tag name
    :param uid: tag uid
    :return: tuple with tag name and uid
    """
    if name == 'Bank and Cards':
        name = 'Finance'
    elif name == 'Education and blogs':
        name = 'Education'
    elif name == 'Other Cards':
        name = 'Other'
    return name.lower(), uid


def import_tags(db: Database, folder_list: list):
    """
    Create the tag table from the database folder list.
    :param db: database
    :param folder_list: list of folders/tags
    :return:
    """
    # Iterate over all the folder definitions and create the dictionary with the mapping
    for folder in folder_list:
        t_name, t_uid = process_tag(folder['title'], folder['uuid'])
        tag_dict[t_uid] = (t_name, TagTableUid.get_uid())

    # Clear the tag uid couters to avoid duplicate uids.
    TagTableUid.clear()

    # Add the tags to the table
    for key in tag_dict:
        t_name, t_uid = tag_dict[key]
        db.tag_table.add(t_name, t_uid)
    db.tag_table.add(TAG_DEFAULT)
    # db.tag_table.dump()


def import_fields(db: Database, item_list: list):
    """
    Create the field table from the field names in the database entries (items)
    :param db: database
    :param item_list: list of items
    """
    for item in item_list:
        for field in item['fields']:
            try:
                f_name, _, f_sensitive = process_field(field)
                db.field_table.add(f_name, f_sensitive)
            except (ValueError, KeyError):
                pass
    # db.field_table.dump()


def import_items(db: Database, item_list: list, encrypt_key: Crypt | None):
    """
    Import all items into the database. This is where the important data gets processed.
    :param db: database
    :param item_list: list of items
    :param encrypt_key: key used to encrypt sensitive values (optional)
    """
    # found = False
    for item in item_list:

        # An item should be a dictionary
        assert isinstance(item, dict)

        # Initialize item data
        item_name = ''
        note = ''
        time_stamp = ''
        folder_list = []
        # field_list = []
        field_collection = FieldCollection()

        # Loop over all items
        for key in item.keys():
            value = item[key]
            if key == 'title':
                item_name = trimmed_string(value)
            elif key == 'createdAt':
                time_stamp = int(trimmed_string(str(value)))
            elif key == 'note':
                note = value
            elif key == 'folders':  # list
                for folder in value:
                    tag_uid = tag_dict[folder][1]
                    if db.tag_table.get_name(tag_uid):
                        db.tag_table.increment(uid=tag_uid)
                        folder_list.append(tag_uid)
            elif key == 'fields':  # list
                for field in value:
                    try:
                        f_name, f_value, f_sensitive = process_field(field)
                        if f_sensitive and encrypt_key is not None:
                            f_value = encrypt_key.encrypt_str2str(str(f_value))
                        field_collection.add(Field(f_name, f_value, f_sensitive))
                        # if 'Network_password' in f_name:
                        #     found = True
                        db.field_table.increment(name=f_name)
                    except ValueError:
                        # can be safely ignored
                        continue

        # if found:
        #     print(item_name)
        #     found = False

        # Assign a default tag list for items with no tag
        if len(folder_list) == 0:
            folder_list = [db.tag_table.get_uid(TAG_DEFAULT)]
            db.tag_table.increment(name=TAG_DEFAULT)

        # An item must have at least a name, a time stamp and at least one field
        if item_name and time_stamp and len(field_collection) > 0:
            item = Item(item_name, folder_list, note, time_stamp, field_collection)
            db.item_collection.add(item)
        else:
            raise ValueError('incomplete item')


def save_tables(db: Database):
    """
    Save the field and tag tables to csv files
    :param db: database
    """
    # Field table
    with open(FIELD_FILE_NAME, 'w') as f:
        for f_name, f_uid, f_count, f_sensitive in db.field_table.next():
            f.write(f'{f_name},{f_uid},{str(f_count)},{f_sensitive}\n')
        f.close()

    # Tag table
    with open(TAG_FILE_NAME, 'w') as f:
        for t_name, t_uid, t_count in db.tag_table.next():
            f.write(f'{t_name},{t_uid},{str(t_count)}\n')
        f.close()


def import_database(input_file_name: str, output_file_name: str, password: str, dump_database=False):
    """
    Import database and write output database
    :param input_file_name: database to import
    :param output_file_name: output database
    :param password: password to encrypt the database (no encryption if blank)
    :param dump_database: print imported database to the standard output
    """
    with open(input_file_name, 'r') as f:
        json_data = json.load(f)
    f.close()

    assert isinstance(json_data, dict)

    # Create the database
    db = Database(output_file_name, password)

    # Process the different sections
    import_tags(db, json_data['folders'])
    import_fields(db, json_data['items'])
    import_items(db, json_data['items'], db.crypt_key)
    save_tables(db)

    # Write file to disk
    db.write()

    # Dump database
    if dump_database:
        db.dump()


if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser(description='Import Enpass database')

    parser.add_argument('input_file',
                        action='store',
                        type=str,
                        help='Input file name in JSON format')

    parser.add_argument('-o', '--output',
                        dest='output_file',
                        action='store',
                        type=str,
                        default=DEFAULT_DATABASE_NAME,
                        help='Output database file')

    parser.add_argument('-d',
                        dest='dump',
                        action='store_true',
                        help='Print output database to stdout')

    # args = parser.parse_args(['pdb.json'])
    args = parser.parse_args()

    # Get the password to encrypt the output database
    input_password = get_password()

    # Import the data
    try:
        import_database(args.input_file, args.output_file, input_password, dump_database=args.dump)
    except Exception as e:
        print(f'Error while importing file {e}')
