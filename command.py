import re
from os.path import exists
from typing import Optional
from db import Database, DEFAULT_DATABASE_NAME
from items import Item, Field
from utils import get_password, timestamp_to_time, print_line, sensitive_mark, trace, todo


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
            print(f'Error: {label} -> {e}')

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
        if self.db_loaded(msg_flag=False) and not self.confirm():
            return
        if exists(file_name):
            self.error(f'database {file_name} already exists')
            return
        self.file_name = file_name
        self.db = Database(file_name, get_password())

    def database_read(self, file_name: str):
        """
        Read database into memory
        :param file_name: database file name
        :return:
        """
        trace('database_read', file_name)
        if self.db_loaded(msg_flag=False) and not self.confirm():
            return

        # Read the database
        self.db = Database(file_name, get_password())
        self.file_name = file_name
        try:
            self.db.read()
        except Exception as e:
            self.error(f'failed to read database {file_name}', e)

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
        trace('field_dump')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.field_table.dump()

    # -----------------------------------------------------------------
    # Item commands
    # -----------------------------------------------------------------

    def item_list(self):
        trace('item_list')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for item in self.db.item_collection.next():
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def item_print(self, uid: int):
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
                    print(f'Date: {timestamp_to_time(item.get_timestamp())}')
                    tag_list = [self.db.tag_table.get_name(x) for x in item.get_tags()]
                    print(f'Tags: {tag_list}')
                    for field in item.next_field():
                        assert isinstance(field, Field)
                        f_sensitive = field.get_sensitive()
                        if f_sensitive and self.db.crypt_key:
                            field_value = self.db.crypt_key.decrypt_str2str(field.get_value())
                        else:
                            field_value = field.get_value()
                        print(f'   {field.get_id()} {sensitive_mark(f_sensitive)} {field.get_name()} {field_value}')
                    print('Note:')
                    if len(item.get_note()) > 0:
                        print(f'{item.get_note()}')
                except Exception as e:
                    self.error(f'cannot print item {uid}', e)
                print_line()
            else:
                self.error(f'item {uid} not found')

    def item_count(self):
        trace('item_count')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.item_collection))

    def item_search(self, name: str, name_flag: bool, tag_flag: bool,
                    field_name_flag: bool, field_value_flag: bool, note_flag: bool):
        trace('item_search', name, name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)
        if self.db_loaded():
            assert isinstance(self.db, Database)
            item_list = self.db.search(name, item_name_flag=name_flag, tag_flag=tag_flag,
                                       field_name_flag=field_name_flag, field_value_flag=field_value_flag,
                                       note_flag=note_flag)
            for item in item_list:
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def item_delete(self, uid: int):
        trace('item_count')
        if self.db_loaded():
            assert isinstance(self.db, Database)
            todo('item_delete', uid)

    def item_dump(self, uid: int):
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


if __name__ == '__main__':
    cp = CommandProcessor()
    cp.database_read(DEFAULT_DATABASE_NAME)
    cp.item_list()
    cp.item_dump(2710)
