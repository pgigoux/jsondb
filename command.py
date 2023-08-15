from db import Database, DEFAULT_DATABASE_NAME
from items import Item, Field
from utils import get_password, timestamp_to_time


class CommandProcessor:

    def __init__(self):
        self.file_name = ''
        self.db = None

    @staticmethod
    def print_line():
        print(u'\u2015' * 70)

    def db_loaded(self, msg_flag=True) -> bool:
        """
        Check whether there's a database in memory
        :return: True if that's the case, False otherwise
        """
        if self.db is None:
            if msg_flag:
                print('no database loaded')
            return False
        else:
            return True

    # -----------------------------------------------------------------
    # Database commands
    # -----------------------------------------------------------------

    def create_database(self, file_name=DEFAULT_DATABASE_NAME):
        """
        Create an empty database
        :param file_name: database file name
        """
        self.file_name = file_name
        self.db = Database(file_name, get_password())

    def read_database(self, file_name: str):
        """
        Read database into memory
        :param file_name: database file name
        :return:
        """
        # Make sure we are not overwriting an existing database
        if self.db_loaded(msg_flag=False):
            print('There is a database already in memory')
            answer = input('Do you want to overwrite it (yes/no)? ')
            if answer not in ['yes']:
                return

        # Read the database
        self.db = Database(file_name, get_password())
        self.file_name = file_name
        try:
            self.db.read()
        except Exception as e:
            print('Failed to read database', repr(e))

    def dump_database(self):
        """
        Dump database contents to the terminal
        :return:
        """
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.print_line()
            self.db.dump()
            self.print_line()

    # -----------------------------------------------------------------
    # Tag commands
    # -----------------------------------------------------------------

    def tag_list(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for t_uid, t_name, t_count in self.db.tag_table.next():
                print(f'{t_uid} {t_name} {t_count}')

    def tag_dump(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.tag_table.dump()

    def tag_count(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.tag_table))

    # -----------------------------------------------------------------
    # Field commands
    # -----------------------------------------------------------------

    def field_list(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for f_uid, f_name, f_count, f_sensitive in self.db.field_table.next():
                print(f'{f_uid} {f_name} {f_count} {f_sensitive}')

    def field_dump(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.field_table.dump()

    def field_count(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.field_table))

    # -----------------------------------------------------------------
    # Item commands
    # -----------------------------------------------------------------

    def item_list(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for item in self.db.item_collection.next():
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def item_print(self, uid: int):
        print('print_item', uid)
        if self.db_loaded():
            self.print_line()
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
                        mark = '(*)' if field.get_sensitive() else '   '
                        if field.get_sensitive() and self.db.crypt_key:
                            field_value = self.db.crypt_key.decrypt_str2str(field.get_value())
                        else:
                            field_value = field.get_value()
                        print(f'   {field.get_id()} {mark} {field.get_name()} {field_value}')
                    print('Note:')
                    if len(item.get_note()) > 0:
                        print(f'{item.get_note()}')
                except Exception as e:
                    print(f'error: {repr(e)}')
                self.print_line()
            else:
                print('item not found')

    def item_dump(self, uid: int):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            if uid in self.db.item_collection:
                item = self.db.item_collection.get(uid)
                assert isinstance(item, Item)
                self.print_line()
                item.dump()
                self.print_line()
            else:
                print('item not found')

    def item_count(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            print(len(self.db.item_collection))

    def item_search(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.search()
            pass


if __name__ == '__main__':
    cp = CommandProcessor()
    cp.read_database(DEFAULT_DATABASE_NAME)
    cp.item_list()
    cp.item_dump(2710)
