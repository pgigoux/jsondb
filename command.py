import re
from os.path import exists
from typing import Optional

from db import Database, DEFAULT_DATABASE_NAME
from items import Item, Field, FieldCollection
from utils import get_password, get_timestamp, timestamp_to_string, print_line, sensitive_mark, trace
from uid import TagTableUid, FieldTableUid, FieldUid, ItemUid


class CommandProcessor:

    def __init__(self):
        """
        The command processor handles the commands that interact with the database
        """
        self.file_name = ''  # database file name
        self.db = None  # database object

    def db_loaded(self, msg_flag=True) -> bool:
        """
        Check whether there's a database in memory
        :return: True if that's the case, False otherwise
        """
        if self.db is None:
            if msg_flag:
                self.error('no database loaded', None)
            return False
        else:
            return True

    @staticmethod
    def error(label: str, e: Optional[Exception] = None):
        """
        Report an error and the optional exception
        :param label: error message
        :param e: exception associated to the error (optional)
        :return:
        """
        if e is None:
            print(f'Error: {label}')
        else:
            print(f'Error: {label} - {e}')

    @staticmethod
    def confirm() -> bool:
        print('There is a database already in memory')
        answer = input('Do you want to overwrite it (yes/no)? ')
        return answer == 'yes'

    # -----------------------------------------------------------------
    # Database commands
    # -----------------------------------------------------------------

    def database_create(self, file_name=DEFAULT_DATABASE_NAME):
        """
        Create an empty database
        :param file_name: database file name
        """
        trace('database_create', file_name)

        # Check whether there's a database already in memory
        # and ask for confirmation to overwrite if that's the case.
        if self.db_loaded(msg_flag=False) and not self.confirm():
            return

        # Check whether the file exists already.
        # Create an empty database if that's not the case.
        if exists(file_name):
            self.error(f'database {file_name} already exists')
        else:
            self.file_name = file_name
            self.db = Database(file_name, get_password())

    def database_read(self, file_name: str):
        """
        Read database into memory
        :param file_name: database file name
        :return:
        """
        trace('database_read', file_name)

        # Check whether there's a database already in memory
        # and ask for confirmation to overwrite if that's the case.
        if self.db_loaded(msg_flag=False) and not self.confirm():
            return

        # Read the database
        try:
            self.db = Database(file_name, get_password())
            self.file_name = file_name
            self.db.read()
        except Exception as e:
            self.error(f'failed to read database {file_name}', e)

    def database_write(self):
        trace('database_write')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.write()
            except Exception as e:
                self.error('cannot write database', e)

    def database_export(self, file_name: str):
        trace('database_export', file_name)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.export_to_json(file_name)
            except Exception as e:
                self.error('cannot export database', e)

    def database_dump(self):
        """
        Dump database contents to the terminal
        :return:
        """
        trace('database_dump')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print_line()
            self.db.dump()
            print_line()

    # -----------------------------------------------------------------
    # Tag commands
    # -----------------------------------------------------------------

    def tag_list(self):
        """
        List all tags
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for t_uid, t_name, t_count in self.db.tag_table.next():
                print(f'{t_uid} {t_count:4d} {t_name}')

    def tag_count(self):
        """
        Print tag count (or how many there are)
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.tag_table))

    def tag_add(self, name: str):
        """
        Add new tag
        :param name:
        :return:
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.tag_table.add(name)
            except Exception as e:
                self.error(f'cannot add tag {name}', e)

    def tag_rename(self, old_name: str, new_name: str):
        """
        Rename existing tag
        :param old_name: old tag name
        :param new_name: new tag name
        :return:
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.tag_table.rename(old_name, new_name)
            except Exception as e:
                self.error(f'cannot rename tag {old_name} to {new_name}', e)

    def tag_delete(self, name: str):
        """
        Delete tag
        :param name: tag name
        :return:
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.tag_table.remove(name=name)
            except Exception as e:
                self.error(f'cannot delete tag {name}', e)

    def tag_dump(self):
        """
        Dump tag table
        :return:
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.tag_table.dump()

    # -----------------------------------------------------------------
    # Field commands
    # -----------------------------------------------------------------

    def field_list(self):
        """
        List all fields
        """
        trace('field_list')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for f_uid, f_name, f_count, f_sensitive in self.db.field_table.next():
                print(f'{f_uid} {f_count:4d} {sensitive_mark(f_sensitive)} {f_name}')

    def field_count(self):
        """
        Print field count (or how many there are)
        """
        trace('field_count')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.field_table))

    def field_search(self, pattern: str):
        """
        Search for fields matching a pattern
        :param pattern: regexp pattern
        """
        trace('field_search', pattern)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for f_uid, f_name, f_count, f_sensitive in self.db.field_table.next():
                if re.search(pattern, f_name):
                    print(f'{f_uid} {f_count:4d} {sensitive_mark(f_sensitive)} {f_name}')

    def field_add(self, name: str, sensitive_flag: bool):
        """
        Add new field
        :param name: field name
        :param sensitive_flag: sensitive?
        :return:
        """
        trace('field_add', name, sensitive_flag)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.field_table.add(name=name, sensitive=sensitive_flag)
            except Exception as e:
                self.error('cannot add field {name}', e)

    def field_delete(self, name: str):
        """
        Delete field from field table
        :param name: field name
        """
        trace('field_delete', name)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.field_table.remove(name=name)
            except Exception as e:
                self.error('cannot remove field {name}', e)

    def field_dump(self):
        """
        Dump the field table
        """
        trace('field_dump')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.field_table.dump()

    # -----------------------------------------------------------------
    # Item commands
    # -----------------------------------------------------------------

    def item_list(self):
        """
        List all items
        """
        trace('item_list')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for item in self.db.item_collection.next():
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def item_print(self, uid: int, show_sensitive: bool):
        """
        Print item
        :param uid: item uid
        :param show_sensitive: print sensitive fields unencrypted
        """
        trace('print_item', uid)
        if self.db_loaded():
            print_line()
            assert isinstance(self.db, Database)
            if uid in self.db.item_collection:
                try:
                    item = self.db.item_collection.get(uid)
                    assert isinstance(item, Item)
                    print(f'UID:  {item.get_id()}')
                    print(f'Name: {item.get_name()}')
                    print(f'Date: {timestamp_to_string(item.get_timestamp())}')
                    print(f'Tags: {self.db.tag_table.get_tag_name_list(item.get_tags())}')
                    print('Fields:')
                    for field in item.next_field():
                        assert isinstance(field, Field)
                        f_value = field.get_decrypted_value(self.db.crypt_key) if show_sensitive else field.get_value()
                        f_sensitive = field.get_sensitive()
                        print(f'   {field.get_id()} {sensitive_mark(f_sensitive)} {field.get_name()} {f_value}')
                    print('Note:')
                    if len(item.get_note()) > 0:
                        print(f'{item.get_note()}')
                except Exception as e:
                    self.error(f'cannot print item {uid}', e)
                print_line()
            else:
                self.error(f'item {uid} not found')

    def item_count(self):
        """
        Print the number of items
        :return:
        """
        trace('item_count')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.item_collection))

    def item_search(self, pattern: str, name_flag: bool, tag_flag: bool,
                    field_name_flag: bool, field_value_flag: bool, note_flag: bool):
        """
        Search for a string pattern in all items.
        :param pattern: pattern to search for
        :param name_flag: search in name?
        :param tag_flag: search in tags?
        :param field_name_flag: search in field names?
        :param field_value_flag: search in field values?
        :param note_flag: search in note?
        """
        trace('item_search', pattern, name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            item_list = self.db.search(pattern, item_name_flag=name_flag, tag_flag=tag_flag,
                                       field_name_flag=field_name_flag, field_value_flag=field_value_flag,
                                       note_flag=note_flag)
            for item in item_list:
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def item_delete(self, uid: int):
        """
        Delete item
        :param uid: item uid
        """
        trace(f'item_delete {uid}')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                self.db.item_collection.remove(uid)
            except Exception as e:
                self.error('error while removing item', e)

    def item_create(self, item_name: str, tag_list: list, field_list, note: str, multiline_note: bool):
        """
        Create new item
        :param item_name:
        :param tag_list:
        :param field_list:
        :param note:
        :param multiline_note:
        """
        trace('item_create')
        if self.db_loaded():
            assert isinstance(self.db, Database)

            # Make sure the name is specified
            if not item_name:
                self.error('item name is required')
                return

            # Process tags
            try:
                tag_uid_list = self.db.tag_table.get_tag_uid_list(tag_list)
            except Exception as e:
                self.error(f'Error while processing tag list', e)
                return
            trace(f'tag uid list {tag_uid_list}')

            # Process fields
            fc = FieldCollection()
            f_name = ''
            try:
                for f_name, f_value in field_list:
                    fc.add(Field(f_name, f_value, self.db.field_table.is_sensitive(name=f_name)))
            except Exception as e:
                self.error(f'Error while adding field {f_name}', e)
                return
            trace('field collection', fc)

            try:
                item = Item(item_name, tag_uid_list, note, fc, time_stamp=get_timestamp())
                # item.dump()
                self.db.item_collection.add(item)
                print(f'Added item {item.get_id()}')
            except Exception as e:
                self.error(f'Error while adding item {item_name}', e)

    def item_add(self, uid: int, item_name: str, tag_list: list,
                 field_list: list, note: str, multiline_note: bool):
        """
        Add item
        :param uid: item uid
        :param item_name: item name
        :param tag_list: tag list
        :param field_list: list of tuples with the field,value pairs to add/edit
        :param note: item note
        :param multiline_note: multiline note?
        """
        self.item_add_edit(uid, item_name, tag_list, field_list, [], note, multiline_note, add_flag=True)

    def item_edit(self, uid: int, item_name: str, tag_list: list,
                  field_list: list[tuple], field_delete_list: list,
                  note: str, multiline_note: bool):
        """
        Edit item
        :param uid: item uid
        :param item_name: item name
        :param tag_list: tag list
        :param field_list: list of tuples with the field,value pairs to add/edit
        :param field_delete_list: list of field names to delete
        :param note: item note
        :param multiline_note: multiline note?
        """
        self.item_add_edit(uid, item_name, tag_list, field_list, field_delete_list, note, multiline_note)

    def item_add_edit(self, uid: int, item_name: str, tag_list: list,
                      field_list: list, field_delete_list: list,
                      note: str, multiline_note: bool,
                      add_flag: Optional[bool] = False):
        """
        Edit existing item
        :param uid: item uid
        :param item_name: item name
        :param tag_list: tag list
        :param field_list: list of tuples with the field,value pairs to add/edit
        :param field_delete_list: list of field names to delete
        :param note: item note
        :param multiline_note: multiline note?
        :param add_flag: allow adding items? (used for tags only)
        """
        trace('item_edit', uid)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                item = self.db.item_collection.get(uid)
                assert isinstance(item, Item)
            except Exception as e:
                self.error(f'item {uid} does not exist', e)
                return

            # Set new name and note
            new_name = item_name if item_name else item.get_name()
            new_note = note if note else item.get_note()
            trace(f'new name={new_name}, note={new_note}')

            # Process tags
            if tag_list:
                try:
                    tag_uid_list = self.db.tag_table.get_tag_uid_list(tag_list)
                    if add_flag:
                        new_tag_list = list(set(tag_uid_list + item.get_tags()))
                    else:
                        new_tag_list = tag_uid_list
                except Exception as e:
                    self.error(f'Error while processing tag list', e)
                    return
            else:
                new_tag_list = item.get_tags()
            trace(f'new tag list {new_tag_list}')

            # Process fields
            field_dict = {k: v for k, v in field_list}
            trace('field_dict', field_dict)
            fc = FieldCollection()
            try:
                # Iterate over all the fields in the existing item
                for field in item.next_field():
                    assert isinstance(field, Field)
                    f_name, f_value, f_sensitive = field.get_name(), field.get_value(), field.get_sensitive()

                    # Skip fields that should be deleted
                    if f_name in field_delete_list:
                        trace('skipped', f_name)
                        continue

                    # Add fields to the new field collection
                    # Use the (new) value from the field_ dict if the field is there
                    # Otherwise keep the old value
                    trace('existing field', f_name, f_value, f_sensitive)
                    if f_name in field_dict:
                        fc.add(Field(f_name, field_dict[f_name], f_sensitive))
                        trace(f'field value for {f_name} updated from {f_value} to {field_dict[f_name]}')
                        del field_dict[f_name]  # remove used field
                    else:
                        trace(f'field value for {f_name} preserved {f_value}')
                        fc.add(Field(f_name, f_value, f_sensitive))

                # Add any fields in the field_dict that were not processed already
                # This will done regardless of the value of the add flag
                for f_name in field_dict:
                    f_sensitive = self.db.field_table.is_sensitive(name=f_name)
                    trace(f'adding new field {f_name} {field_dict[f_name]}, {f_sensitive}')
                    fc.add(Field(f_name, field_dict[f_name], f_sensitive))

            except Exception as e:
                print(e)

            # Create the new item
            try:
                new_item = Item(new_name, new_tag_list, new_note, fc, time_stamp=get_timestamp(), uid=item.get_id())
                new_item.dump()
                self.db.item_collection.update(new_item)
            except Exception as e:
                self.error('error when creating item', e)
                return

    def item_copy(self, uid: int):
        """
        Create a copy of an item with a different uid
        The field collection is recreated and the timestamp updated.
        :param uid: item uid
        """
        trace('item_copy', uid)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            try:
                item = self.db.item_collection.get(uid)
                assert isinstance(item, Item)
                fc = FieldCollection()
                for field in item.field_collection.next():
                    assert isinstance(field, Field)
                    f_name, f_value, f_sensitive = field.get_name(), field.get_value(), field.get_sensitive()
                    fc.add(Field(f_name, f_value, f_sensitive))
                new_item = Item('Copy of ' + item.get_name(), item.get_tags(), item.get_note(), fc,
                                uid=ItemUid.get_uid())
                trace('new item', new_item)
                self.db.item_collection.add(new_item)
                print(f'create item {new_item.get_id()} from {item.get_id()}')
            except Exception as e:
                print('cannot make copy of item', e)

    def item_dump(self, uid: int):
        """
        Dump item contents
        :param uid: item uid
        """
        trace('item_dump', uid)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            if uid in self.db.item_collection:
                item = self.db.item_collection.get(uid)
                assert isinstance(item, Item)
                print_line()
                item.dump()
                print_line()
            else:
                self.error(f'item {uid} not found')

    # -----------------------------------------------------------------
    # Misc commands
    # -----------------------------------------------------------------

    def quit_command(self, keyboard_interrupt: bool):
        """
        Command that will be called when the program exits
        """
        trace(f'quit_command {self.file_name}', keyboard_interrupt)

    def report(self):
        """
        Print a database report
        """
        if self.db_loaded():
            print(f'Tag table:         {len(self.db.tag_table)}')
            print(f'Field table:       {len(self.db.field_table)}')
            print(f'Items collection:  {len(self.db.item_collection)}')
            print('Unique identifiers')
            print(f'\tTag table    {TagTableUid.to_str()}')
            print(f'\tField table  {FieldTableUid.to_str()}')
            print(f'\tItems        {ItemUid.to_str()}')
            print(f'\tFields       {FieldUid.to_str()}')


if __name__ == '__main__':
    cp = CommandProcessor()
    cp.database_read(DEFAULT_DATABASE_NAME)
    cp.item_list()
    cp.item_dump(2710)
