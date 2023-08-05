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
        self.command = ''
        self.cmd = CommandProcessor()

    def error(self, error_message: str, token: Token, value: Union[int, float, str]):
        if token == Token.UNTERMINATED:
            print(f'Unterminated string {self.command}')
        elif token == Token.INVALID:
            print(f'Invalid token {token} {value}')
        else:
            print(f'{error_message} {token} {value}')

    # @staticmethod
    # def invalid(token: Token) -> bool:
    #     return token in [Token.INVALID, Token.UNTERMINATED]

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
        input_output_command: READ [file_name] |
                              WRITE |
                              export file_name
        """
        trace('input_output_command', token)
        if token == Token.READ:
            token, value = self.get_token()
            if token == Token.EOS:
                todo('read, no file name')
                # self.cmd.read_database()
            elif token == Token.FILE:
                todo('read', value)
                # self.cmd.read_database(value)
            else:
                self.error('bad file name', token, value)
        elif token == Token.WRITE:
            trace('input_output', 'write')
        elif token == Token.EXPORT:
            token, value = self.get_token()
            trace('input_output', 'export', token, value)
            if token == Token.FILE:
                todo(''
                     '', 'export', token, value)
            else:
                self.error('missing file name', token, value)
        else:
            self.error('Unknown i/o command', token, '')

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

    def process_command(self):
        """
        A command can be either an action or i/o command
        command : action_command |
                  input_output_command
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
        elif token == Token.EOS:
            pass
        else:
            self.error('Unknown command', token, value)

    def execute(self, command: str):
        """
        Parse and execute command
        :param command: command to parse/execute
        """
        self.command = command.strip()
        self.lexer.input(self.command)
        self.process_command()


if __name__ == '__main__':
    parser = Parser()
    while True:
        try:
            cmd = input('db> ')
            cmd = cmd.strip()
            if len(cmd) > 0:
                parser.execute(cmd)
        except (KeyboardInterrupt, EOFError):
            break
