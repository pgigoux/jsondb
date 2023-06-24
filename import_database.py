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
from db import Database
from items import FieldCollection, Item, Field
from utils import trimmed_string, get_password


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
        raise ValueError('empty field')
    if f_name in ['508', 'If lost, call']:
        raise ValueError('ignored name')

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
    elif f_name == 'Expiry date':
        f_name = 'Expiration date'
    elif f_name == 'MAC/Airport #':
        f_name = 'MAC #'
    elif 'Security answer' in f_name:
        f_sensitive = True

    return f_name, f_value, f_sensitive


def import_tags(db: Database, folder_list: list):
    """
    Create the tag table from the database folder list.
    :param db: database
    :param folder_list:
    :return:
    """
    for folder in folder_list:
        db.tag_table.add(folder['title'], folder['uuid'])


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


def import_items(db: Database, item_list: list):
    """
    Import all items into the database. This is where the important data gets processed.
    :param db: database
    :param item_list: list of items
    """
    for item in item_list:

        # An item should be a dictionary
        assert isinstance(item, dict)

        # Initialize item data
        name = ''
        note = ''
        time_stamp = ''
        folder_list = []
        # field_list = []
        field_collection = FieldCollection()

        # Loop over all items
        for key in item.keys():
            value = item[key]
            if key == 'title':
                name = trimmed_string(value)
            elif key == 'createdAt':
                time_stamp = int(trimmed_string(str(value)))
            elif key == 'note':
                note = value
            elif key == 'folders':  # list
                for folder in value:
                    if db.tag_table.get_name(folder):
                        folder_list.append(folder)
            elif key == 'fields':  # list
                for field in value:
                    try:
                        f_name, f_value, f_sensitive = process_field(field)
                        field_collection.add(Field(f_name, f_value, f_sensitive))
                    except ValueError:
                        # can be safely ignored
                        continue

        # An item must have at least a name, a time stamp and at least one field
        if name and time_stamp and len(field_collection) > 0:
            item = Item(name, folder_list, note, time_stamp, field_collection)
            db.add_item(item)
        else:
            raise ValueError('incomplete item')


def import_database(input_file_name: str, output_file_name: str, password: str, dump_database=False):
    """
    Import database and write output database
    :param input_file_name: database to import
    :param output_file_name: output database
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
    import_items(db, json_data['items'])

    # Write file to disk
    db.write()

    # Dump database
    if dump_database:
        db.dump()


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Import Enpass database')
    parser.add_argument('input_file', type=str, help='Input file name in JSON format')
    parser.add_argument('output_file', type=str, help='Output database file')
    parser.add_argument('-d', dest='dump', action='store_true', help='Dump output database')
    args = parser.parse_args()

    # Get the password to encrypt the output database
    password = get_password()

    # Import the data
    try:
        import_database(args.input_file, args.output_file, password, dump_database=args.dump)
    except Exception as e:
        print(f'Error while importing file {e}')
