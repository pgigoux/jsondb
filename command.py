from db import Database, DEFAULT_DATABASE_NAME
from utils import get_password


class CommandProcessor:

    def __init__(self):
        self.file_name = ''
        self.db = None

    def db_loaded(self) -> bool:
        """
        Check whether there's a database in memory
        :return: True if that's the case, False otherwise
        """
        return self.db is None

    def create_database(self, file_name=DEFAULT_DATABASE_NAME):
        """
        Create an empty database
        :param file_name: database file name
        """
        self.file_name = file_name
        self.db = Database(file_name, get_password())

    def read_database(self, file_name=DEFAULT_DATABASE_NAME):
        """
        Read database into memory
        :param file_name: database file name
        :return:
        """
        # Make sure we are not overwriting an existing database
        if self.db_loaded():
            print('There is a database in memory already')
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


if __name__ == '__main__':
    cp = CommandProcessor()
