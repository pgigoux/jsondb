from db import Database, DEFAULT_DATABASE_NAME
from utils import get_password


class CommandProcessor:

    def __init__(self):
        self.file_name = ''
        self.db = None

    def read_database(self) -> bool:
        """
        Read database into memory
        :return:
        """
        self.db = Database(self.file_name, get_password())
        try:
            self.db.read()
            return True
        except FileNotFoundError:
            print(f'File {self.file_name} does not exist')
        except ValueError:
            print('Failed to read database')
        return False

    def no_database(self) -> bool:
        """
        Check whether there's a database in memory
        :return: True if that's the case, False otherwise
        """
        if self.db is None:
            print('No database loaded')
            return False
        else:
            return True

    def read_command(self, file_name=DEFAULT_DATABASE_NAME):

        # Make sure we are not overwriting the database
        if not self.no_database():
            print('There is a database in memory already')
            answer = input('Do you want to overwrite it (yes/no)? ')
            if answer not in ['yes']:
                return

        # Read the database
        self.db = Database(file_name, get_password())
        self.file_name = file_name
        try:
            self.db.read()
            return
        except Exception as e:
            print('Failed to read database', repr(e))


if __name__ == '__main__':
    cp = CommandProcessor()
