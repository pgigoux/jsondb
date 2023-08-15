from typing import Union
from db import DEFAULT_DATABASE_NAME
from command import CommandProcessor
from lexer import Lexer, Token, LEX_ACTIONS, LEX_SUBCOMMANDS, LEX_DATABASE


def trace(label: str, *args):
    print(f'{label}: ' + str([f'{x}' for x in args]))


def todo(label: str, *args):
    print(f'RUN: {label}: ' + str([f'{x}' for x in args]))


# Error messages
ERROR_UNKNOWN_COMMAND = 'unknown command'
ERROR_UNKNOWN_SUBCOMMAND = 'unknown subcommand'
ERROR_BAD_FILENAME = 'bad file name'


class Parser:
    """
    Recursive descent parser to process commands
    """

    def __init__(self):
        self.lexer = Lexer()
        self.cmd = ''
        self.cp = CommandProcessor()

    @staticmethod
    def error(error_message: str, token: Token, value: Union[int, float, str]):
        """
        Print error message
        :param error_message: message text
        :param token: offending token
        :param value: token value
        :return:
        """
        if token == Token.INVALID:
            print(f'Invalid token {token} {value}')
        else:
            print(f'{error_message} {token} {value}')

    def get_token(self) -> tuple[Token, Union[str, int, float]]:
        """
        Get next token from the lexer
        :return: token id and value
        """
        token, value = self.lexer.next_token()
        print(f'get_token: {token} {value}')
        return token, value

    def field_command(self, token: Token, value: str):
        """
        field_command : FIELD subcommand
        :param token: subcommand token
        :param value: subcommand value
        """
        trace('field_command', token)
        if token == Token.LIST:
            self.cp.field_list()
        elif token == Token.DUMP:
            self.cp.field_dump()
        elif token == Token.COUNT:
            self.cp.field_count()
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token, value)

    def tag_command(self, token: Token, value: str):
        """
        tag_command : TAG subcommand
        :param token: subcommand token
        :param value: subcommand value
        """
        trace('tag_command', token)
        if token == Token.LIST:
            self.cp.tag_list()
        elif token == Token.DUMP:
            self.cp.tag_dump()
        elif token == Token.COUNT:
            self.cp.tag_count()
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token, value)

    def item_search_command(self):
        """
        item_search_command: ITEM SEARCH NAME search_option_list
        :return:
        """
        tok, value = self.get_token()
        if tok == Token.NAME:
            # Process flags
            name_flag, tag_flag, field_name_flag, field_value_flag, note_flag = (False, False, False, False, False)
            while True:
                tok, _ = self.get_token()
                if tok == Token.EOS:
                    break
                elif tok == Token.SW_NAME:
                    name_flag = True
                elif tok == Token.SW_TAG:
                    tag_flag = True
                elif tok == Token.SW_FIELD_NAME:
                    field_name_flag = True
                elif tok == Token.SW_FIELD_VALUE:
                    field_value_flag = True
                elif tok == Token.SW_NOTE:
                    note_flag = True

            # Enable search by item name if no flags were specified
            if not any((name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)):
                name_flag = True

            self.cp.item_search(value, name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)
        else:
            self.error('name expected', tok, value)

    def item_command(self, token: Token, value: str):
        """
        item_command : ITEM subcommand
        :param token: subcommand token
        :param value: subcommand value
        """
        trace('item_command', token)
        if token == Token.LIST:
            self.cp.item_list()
        elif token in [Token.PRINT, Token.DUMP]:
            tok, uid = self.get_token()
            trace('print,dump', tok, uid)
            if tok == Token.VALUE:
                if token == Token.PRINT:
                    self.cp.item_print(uid)
                else:
                    self.cp.item_dump(uid)
            else:
                print('name expected')
        elif token == Token.COUNT:
            self.cp.item_count()
        elif token == Token.SEARCH:
            self.item_search_command()
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token, value)

    def action_command(self, cmd_token: Token, cmd_value, sub_token: Token, sub_value: str):
        """
        action_command : command subcommand
        :param cmd_token: command token
        :param cmd_value: command value
        :param sub_token: subcommand token
        :param sub_value: subcommand value
        """
        trace('action_command', cmd_token, cmd_value, sub_token, sub_value)
        if cmd_token == Token.ITEM:
            self.item_command(sub_token, sub_value)
        elif cmd_token == Token.FIELD:
            self.field_command(sub_token, sub_value)
        elif cmd_token == Token.TAG:
            self.tag_command(sub_token, sub_value)
        else:
            self.error(ERROR_UNKNOWN_COMMAND, cmd_token, cmd_value)  # should never get here

    def database_commands(self, token: Token, value: str):
        """
        database_commands: CREATE [file_name] |
                              READ [file_name] |
                              WRITE |
                              EXPORT file_name |
                              DUMP
        :param token: next token
        :param value: token value
        """
        trace('input_output_command', token)
        if token in [Token.CREATE, Token.READ]:

            # Get file name
            tok, file_name = self.get_token()
            if tok == Token.EOS:
                file_name = DEFAULT_DATABASE_NAME
                trace('no file name', file_name)
            elif tok == Token.FILE:
                trace('file name', file_name)
            else:
                self.error(ERROR_BAD_FILENAME, token, file_name)
                return

            # Run command
            if token == Token.READ:
                trace('read', file_name)
                self.cp.read_database(file_name)
            elif token == Token.CREATE:
                todo('create', file_name)
            else:
                self.error(ERROR_UNKNOWN_COMMAND, token, value)

        elif token == Token.WRITE:
            trace('input_output', 'write')

        elif token == Token.EXPORT:
            # Get file name and run command
            tok, file_name = self.get_token()
            trace('input_output', 'export', tok, file_name)
            if tok == Token.FILE:
                todo('export', file_name)
            else:
                self.error(ERROR_BAD_FILENAME, token, file_name)
        elif token == Token.DUMP:
            self.cp.dump_database()
        else:
            self.error(ERROR_UNKNOWN_COMMAND, token, value)  # should never get here

    def subcommand(self) -> tuple[Token, Union[str, int, float]]:
        """
        Check whether the next token is a subcommand
        :return: token and value, or Token.INVALID if not i/o
        """
        token, value = self.lexer.next_token()
        trace('subcommand', token, value)
        if token in LEX_SUBCOMMANDS:
            return token, value
        else:
            return Token.INVALID, value

    def command(self) -> bool:
        """
        A command can be either an action or and input/output command
        command : action_command |
                  input_output_command |
                  misc_command
        :return True if the QUIT command is received, False otherwise
        """
        token, value = self.lexer.next_token()
        trace('command', token, value)
        quit_flag = False
        if token in LEX_ACTIONS:
            sub_token, value = self.subcommand()
            if sub_token != Token.INVALID:
                self.action_command(token, value, sub_token, value)
            else:
                self.error('Invalid subcommand', sub_token, value)
        elif token in LEX_DATABASE:
            self.database_commands(token, value)
        elif token == Token.EOS:
            pass
        else:
            self.error(ERROR_UNKNOWN_COMMAND, token, value)
        return quit_flag

    def execute(self, command: str):
        """
        Parse and execute command
        :param command: command to parse/execute
        """
        self.cmd = command.strip()
        self.lexer.input(self.cmd)
        return self.command()

    def quit(self):
        """
        Terminate the parser
        """
        trace('quit')
        self.cp.quit_command()


if __name__ == '__main__':
    parser = Parser()
    while True:
        try:
            input_command = input('db> ')
            input_command = input_command.strip()
            if len(input_command) > 0:
                if parser.execute(input_command):
                    # quit received
                    print('Exiting..')
                    break
        except (KeyboardInterrupt, EOFError):
            break
