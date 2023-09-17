from db import DEFAULT_DATABASE_NAME
from command import CommandProcessor
from lexer import Lexer, Token, Tid, LEX_ACTIONS, LEX_SUBCOMMANDS, LEX_DATABASE, LEX_MISC, LEX_STRINGS
from utils import trace, todo

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
    def error(error_message: str, *args):
        """
        Print error message
        :param error_message: message text
        :param args: arguments
        :return:
        """
        print(f'Error: {error_message}: ' + str([f'{x}' for x in args]))

    def get_token(self) -> Token:
        """
        Get next token from the lexer
        :return: token id and value
        """
        token = self.lexer.next_token()
        trace('get_token', token)
        return token

    def field_command(self, token: Token):
        """
        field_command : FIELD subcommand
        :param token: subcommand token
        """
        trace('field_command', token)
        if token.tid == Tid.LIST:
            self.cp.field_list()
        elif token.tid == Tid.DUMP:
            self.cp.field_dump()
        elif token.tid == Tid.COUNT:
            self.cp.field_count()
        elif token.tid in [Tid.SEARCH, Tid.DELETE]:
            tok = self.get_token()
            if tok.tid in LEX_STRINGS:
                if token.tid == Tid.SEARCH:
                    trace('field search', tok)
                    self.cp.field_search(tok.value)
                else:
                    trace('field delete', tok)
                    self.cp.field_delete(tok.value)
            else:
                self.error('bad/missing field name', tok)
        elif token.tid == Tid.ADD:
            tok = self.get_token()
            trace('field add', tok)
            if tok.tid in LEX_STRINGS:
                s_tok = self.get_token()
                sensitive = True if s_tok.tid == Tid.SW_SENSITIVE else False
                self.cp.field_add(tok.value, sensitive)
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token)

    def tag_command(self, token: Token):
        """
        tag_command : TAG subcommand
        :param token: subcommand token
        """
        trace('tag_command', token)
        if token.tid == Tid.LIST:
            self.cp.tag_list()
        elif token.tid == Tid.DUMP:
            self.cp.tag_dump()
        elif token.tid == Tid.COUNT:
            self.cp.tag_count()
        elif token.tid == Tid.ADD:
            tok = self.get_token()
            if tok.tid in LEX_STRINGS:
                self.cp.tag_add(tok.value)
        elif token.tid == Tid.RENAME:
            tok1 = self.get_token()
            tok2 = self.get_token()
            if tok1.tid in LEX_STRINGS and tok2.tid in LEX_STRINGS:
                self.cp.tag_rename(tok1.value, tok2.value)
            else:
                self.error('bad tag name', tok1, tok2)
        elif token.tid == Tid.DELETE:
            tok = self.get_token()
            if tok.tid in LEX_STRINGS:
                self.cp.tag_delete(tok.value)
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token)

    def item_search_command(self):
        """
        item_search_command: ITEM SEARCH NAME search_option_list
        :return:
        """
        tok = self.get_token()
        trace('item_search_command', tok)
        if tok.tid in LEX_STRINGS:
            pattern = tok.value
            # Process flags
            name_flag, tag_flag, field_name_flag, field_value_flag, note_flag = (False, False, False, False, False)
            while True:
                tok = self.get_token()
                if tok.tid == Tid.EOS:
                    break
                elif tok.tid == Tid.SW_NAME:
                    name_flag = True
                elif tok.tid == Tid.SW_TAG:
                    tag_flag = True
                elif tok.tid == Tid.SW_FIELD_NAME:
                    field_name_flag = True
                elif tok.tid == Tid.SW_FIELD_VALUE:
                    field_value_flag = True
                elif tok.tid == Tid.SW_NOTE:
                    note_flag = True

            # Enable search by item name if no flags were specified
            if not any((name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)):
                name_flag = True

            trace('to search', tok.value, name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)
            self.cp.item_search(pattern, name_flag, tag_flag, field_name_flag, field_value_flag, note_flag)
        else:
            self.error('name expected', tok)

    def item_print(self, token: Token):
        """
        item_print_command: PRINT [SW_SENSITIVE]
        :param token: item token
        """
        tok = self.get_token()
        if tok.tid == Tid.SW_SENSITIVE:
            self.cp.item_print(token.value, True)
        else:
            self.cp.item_print(token.value, False)

    def item_command(self, token: Token):
        """
        item_command : ITEM subcommand
        :param token: subcommand token
        """
        trace('item_command', token)
        if token.tid == Tid.LIST:
            self.cp.item_list()
        elif token.tid in [Tid.PRINT, Tid.DUMP, Tid.DELETE]:
            tok = self.get_token()
            trace('print, dump, delete', tok)
            if tok.tid == Tid.VALUE:
                if token.tid == Tid.PRINT:
                    # self.cp.item_print(tok.value)
                    self.item_print(tok)
                elif token.tid == Tid.DELETE:
                    self.cp.item_delete(tok.value)
                else:
                    self.cp.item_dump(tok.value)
            else:
                self.error('item id expected')
        elif token.tid == Tid.COUNT:
            self.cp.item_count()
        elif token.tid == Tid.SEARCH:
            self.item_search_command()
        elif token.tid == Tid.ADD:
            self.cp.item_add()
        elif token.tid == Tid.EDIT:
            tok = self.get_token()
            if tok.tid == Tid.VALUE:
                self.cp.item_edit(tok.value)
            else:
                self.error('item id expected')
        else:
            self.error(ERROR_UNKNOWN_SUBCOMMAND, token)

    def action_command(self, cmd_token: Token, sub_token: Token):
        """
        action_command : ITEM subcommand |
                         FIELD subcommand |
                         TAG subcommand
        :param cmd_token: command token
        :param sub_token: subcommand token
        """
        trace('action_command', cmd_token, sub_token)
        if cmd_token.tid == Tid.ITEM:
            self.item_command(sub_token)
        elif cmd_token.tid == Tid.FIELD:
            self.field_command(sub_token)
        elif cmd_token.tid == Tid.TAG:
            self.tag_command(sub_token)
        else:
            self.error(ERROR_UNKNOWN_COMMAND, cmd_token)  # should never get here

    def database_commands(self, token: Token):
        """
        database_commands: CREATE [file_name] |
                              READ [file_name] |
                              WRITE |
                              EXPORT file_name |
                              DUMP
        :param token: next token
        """
        trace('database_command', token)
        if token.tid in [Tid.CREATE, Tid.READ]:

            # Get file name
            tok = self.get_token()
            if tok.tid == Tid.EOS:
                file_name = DEFAULT_DATABASE_NAME
                trace('no file name', file_name)
            elif tok.tid == Tid.FILE:
                file_name = tok.value
                trace('file name', file_name)
            else:
                self.error(ERROR_BAD_FILENAME, token)
                return

            # Run command
            if token.tid == Tid.READ:
                trace('read', file_name)
                self.cp.database_read(file_name)
            elif token.tid == Tid.CREATE:
                self.cp.database_create(file_name)
            else:
                self.error(ERROR_UNKNOWN_COMMAND, token)  # should never get here

        elif token.tid == Tid.WRITE:
            todo('write', token.value)

        elif token.tid == Tid.EXPORT:
            tok = self.get_token()
            trace('export', tok)
            if tok.tid == Tid.FILE:
                todo('export', tok.value)
            else:
                self.error(ERROR_BAD_FILENAME, tok)

        elif token.tid == Tid.DUMP:
            self.cp.database_dump()
        else:
            self.error(ERROR_UNKNOWN_COMMAND, token)  # should never get here

    def subcommand(self) -> Token:
        """
        Check whether the next token is a subcommand
        :return: token, or invalid/eos if not subcommand
        """
        token = self.lexer.next_token()
        trace('subcommand', token)
        if token.tid in LEX_SUBCOMMANDS:
            return token
        elif token.tid == Tid.EOS:
            return token
        else:
            return Token(Tid.INVALID, token.value)

    def command(self):
        """
        A command can be either an action or and input/output command
        command : action_command |
                  database_command |
        """
        token = self.lexer.next_token()
        trace('command', token)
        if token.tid in LEX_ACTIONS:
            sub_token = self.subcommand()
            if sub_token.tid not in [Tid.INVALID, Tid.EOS]:
                self.action_command(token, sub_token)
            else:
                self.error('invalid or missing subcommand', sub_token)
        elif token.tid in LEX_DATABASE:
            self.database_commands(token)
        elif token.tid in LEX_MISC:
            self.misc_commands(token)
        elif token.tid == Tid.EOS:
            pass
        else:
            self.error(ERROR_UNKNOWN_COMMAND, token)

    def misc_commands(self, token: Token):
        trace('misc_command', token)
        if token.tid == Tid.REPORT:
            self.cp.report()
        else:
            self.error(ERROR_UNKNOWN_COMMAND, token)

    def execute(self, command: str):
        """
        Parse and execute command
        :param command: command to parse/execute
        """
        self.cmd = command.strip()
        self.lexer.input(self.cmd)
        return self.command()

    def quit(self, keyboard_interrupt: bool):
        """
        Terminate the parser
        :param keyboard_interrupt: program terminated by ctrl-c?
        """
        trace('quit')
        self.cp.quit_command(keyboard_interrupt)


if __name__ == '__main__':
    pass
    # parser = Parser()
    # while True:
    #     try:
    #         input_command = input('db> ')
    #         input_command = input_command.strip()
    #         if len(input_command) > 0:
    #             if parser.execute(input_command):
    #                 # quit received
    #                 print('Exiting..')
    #                 break
    #     except (KeyboardInterrupt, EOFError):
    #         break
