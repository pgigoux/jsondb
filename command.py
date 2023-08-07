from db import Database, DEFAULT_DATABASE_NAME
from items import Item
from utils import get_password


class CommandProcessor:

    def __init__(self):
        self.file_name = ''
        self.db = None

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
            self.db.dump()

    def list_items(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            for item in self.db.item_collection.next():
                assert isinstance(item, Item)
                print(f'{item.get_id()} - {item.name}')

    def print_item(self, uid: str):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            if uid in self.db.item_collection:
                item = self.db.item_collection.get(uid)
                assert isinstance(item, Item)
                item.dump()
            else:
                print('item not found')

    def search_items(self):
        if self.db_loaded():
            assert isinstance(self.db, Database)
            self.db.search()
            pass

if __name__ == '__main__':
    cp = CommandProcessor()
