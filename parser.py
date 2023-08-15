from typing import Union
from db import DEFAULT_DATABASE_NAME
from command import CommandProcessor
from lexer import Lexer, Token, LEX_ACTIONS, LEX_SUBCOMMANDS, LEX_INPUT_OUTPUT, LEX_MISC_COMMANDS


def trace(label: str, *args):
    print(f'{label}: ' + str([f'{x}' for x in args]))


def todo(label: str, *args):
    print(f'RUN: {label}: ' + str([f'{x}' for x in args]))


# Error message when an unimplemented or unknown subcommand is found
UNKNOWN_SUBCOMMAND = 'unknown subcommand'


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

    def field_command(self, token: Token):
        """
        field_command : FIELD subcommand
        :param token: subcommand token
        """
        trace('field_command', token)
        if token == Token.LIST:
            self.cp.field_list()
        elif token == Token.DUMP:
            self.cp.field_dump()
        elif token == Token.COUNT:
            self.cp.field_count()
        else:
            self.error('bad subcommand', token, '')

    def tag_command(self, token: Token):
        """
        tag_command : TAG subcommand
        :param token: subcommand token
        """
        trace('tag_command', token)
        if token == Token.LIST:
            self.cp.tag_list()
        elif token == Token.DUMP:
            self.cp.tag_dump()
        elif token == Token.COUNT:
            self.cp.tag_count()
        else:
            self.error('bad subcommand', token, '')

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

    def item_command(self, token: Token):
        """
        item_command : ITEM subcommand
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
                print('expected uid')
        elif token == Token.COUNT:
            self.cp.item_count()
        elif token == Token.SEARCH:
            self.item_search_command()
        else:
            self.error('bad subcommand', token, '')

    def action_command(self, cmd_token: Token, sub_token: Token):
        """
        action_command : command subcommand
        :param cmd_token: command token
        :param sub_token: subcommand token
        :return:
        """
        trace('action_command', cmd_token, sub_token)
        if cmd_token == Token.ITEM:
            self.item_command(sub_token)
        elif cmd_token == Token.FIELD:
            self.field_command(sub_token)
        elif cmd_token == Token.TAG:
            self.tag_command(sub_token)

    def input_output_command(self, token: Token):
        """
        input_output_command: CREATE [file_name] |
                              READ [file_name] |
                              WRITE |
                              export file_name
        :param token: next token
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
                self.error('bad file name', token, file_name)
                return

            # Run command
            if token == Token.READ:
                trace('read', file_name)
                self.cp.read_database(file_name)
            elif token == Token.CREATE:
                todo('create', file_name)
            else:
                self.error('bad command', token)

        elif token == Token.WRITE:
            trace('input_output', 'write')

        elif token == Token.EXPORT:
            # Get file name and run command
            tok, file_name = self.get_token()
            trace('input_output', 'export', tok, file_name)
            if tok == Token.FILE:
                todo('export', file_name)
            else:
                self.error('missing file name', token, file_name)
        else:
            self.error('Unknown i/o command', token, '')  # should never get here

    def misc_command(self, token: Token) -> bool:
        """
        misc_command: DUMP | QUIT
        :param token: next token
        :return: True if QUIT command, False otherwise
        """
        if token == Token.DUMP:
            self.cp.dump_database()
        elif token == Token.QUIT:
            todo('quit', token)
            return True
        return False

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
                self.action_command(token, sub_token)
            else:
                self.error('Invalid subcommand', sub_token, value)
        elif token in LEX_INPUT_OUTPUT:
            self.input_output_command(token)
        elif token in LEX_MISC_COMMANDS:
            quit_flag = self.misc_command(token)
        elif token == Token.EOS:
            pass
        else:
            self.error('Unknown command', token, value)
        return quit_flag

    def execute(self, command: str):
        """
        Parse and execute command
        :param command: command to parse/execute
        """
        self.cmd = command.strip()
        self.lexer.input(self.cmd)
        return self.command()


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
