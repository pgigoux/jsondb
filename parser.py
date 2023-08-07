from db import DEFAULT_DATABASE_NAME
from command import CommandProcessor
from lexer import Lexer, Token, LEX_ACTIONS, LEX_SUBCOMMANDS, LEX_INPUT_OUTPUT
from typing import Union


def trace(label: str, *args):
    print(f'{label}: ' + str([f'{x}' for x in args]))


def todo(label: str, *args):
    print(f'RUN: {label}: ' + str([f'{x}' for x in args]))


class Parser:

    def __init__(self):
        self.lexer = Lexer()
        self.cmd = ''
        self.cp = CommandProcessor()

    @staticmethod
    def error(error_message: str, token: Token, value: Union[int, float, str]):
        if token == Token.INVALID:
            print(f'Invalid token {token} {value}')
        else:
            print(f'{error_message} {token} {value}')

    def get_token(self) -> tuple[Token, Union[str, int, float]]:
        token, value = self.lexer.next_token()
        print(f'get_token: {token} {value}')
        return token, value

    def field_command(self, token: Token):
        trace('field_command', token)
        pass

    def tag_command(self, token: Token):
        trace('tag_command', token)
        pass

    def item_command(self, token: Token):
        """
        item : ITEM subcommand
        """
        trace('item_command', token)

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
                todo('read', file_name)
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
                  input_output_command
        :return True if the QUIT command is received, False otherwise
        """
        token, value = self.lexer.next_token()
        trace('command', token, value)
        if token in LEX_ACTIONS:
            sub_token, value = self.subcommand()
            if sub_token != Token.INVALID:
                self.action_command(token, sub_token)
            else:
                self.error('Invalid subcommand', sub_token, value)
        elif token in LEX_INPUT_OUTPUT:
            self.input_output_command(token)
        elif token == Token.DUMP:
            todo('dump', token)
        elif token == Token.QUIT:
            todo('quit', token)
            return True
        elif token == Token.EOS:
            pass
        else:
            self.error('Unknown command', token, value)
        return False

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
