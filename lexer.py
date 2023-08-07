import re
from enum import Enum, auto
from typing import Union

# Regular expressions
UID_PATTERN = r'[a-z0-9]*-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+'
LONG_DATE_PATTERN = r'\d\d/\d\d/\d\d\d\d'
SHORT_DATE_PATTERN = r'\d\d/\d\d/\d\d'
MONTH_YEAR_PATTERN = r'\d\d/\d\d'
FILE_PATTERN = r'[a-z0-9]+\.[a-z0-9]+'
NAME_PATTERN = r'[a-zA-Z_][a-zA-Z_0-9]*'
INT_PATTERN = r'\d+'
FLOAT_PATTERN = r'\d*\.\d+'


# Tokens
class Token(Enum):
    # commands
    ITEM = auto()
    FIELD = auto()
    TAG = auto()
    ADD = auto()
    CREATE = auto()
    READ = auto()
    WRITE = auto()
    EXPORT = auto()
    # subcommands
    LIST = auto()
    SEARCH = auto()
    PRINT = auto()
    COUNT = auto()
    RENAME = auto()
    DELETE = auto()
    EDIT = auto()
    # data
    UID = auto()
    NAME = auto()
    FILE = auto()
    VALUE = auto()
    STRING = auto()
    # misc
    DUMP = auto()
    QUIT = auto()
    EOS = auto()
    # error
    INVALID = auto()


# Token classes
LEX_ACTIONS = [Token.ITEM, Token.FIELD, Token.TAG]
LEX_INPUT_OUTPUT = [Token.CREATE, Token.READ, Token.WRITE, Token.EXPORT]
LEX_SUBCOMMANDS = [Token.LIST, Token.PRINT, Token.SEARCH, Token.PRINT,
                   Token.COUNT, Token.RENAME, Token.DELETE, Token.EDIT]
LEX_MISC_COMMANDS = [Token.DUMP, Token.QUIT]


# DFA states
class State(Enum):
    START = auto()
    WORD = auto()
    STRING = auto()


# Valid string delimiters
STRING_DELIMITERS = ['\'', '"']

# Unterminated string error message
UNTERMINATED_STRING = 'unterminated'


class Lexer:

    def __init__(self):
        self.command = ''
        self.count = 0
        self.char_list = []
        self.state = State.START
        self.keywords = {
            'item': Token.ITEM, 'field': Token.FIELD, 'tag': Token.TAG,
            'create': Token.CREATE, 'read': Token.READ, 'write': Token.WRITE, 'export': Token.EXPORT,
            'list': Token.LIST, 'search': Token.SEARCH, 'print': Token.PRINT,
            'count': Token.COUNT, 'rename': Token.RENAME, 'delete': Token.DELETE, 'edit': Token.EDIT,
            'dump': Token.DUMP, 'quit': Token.QUIT,
            # aliases
            'save': Token.WRITE, 'ren': Token.RENAME, 'del': Token.DELETE
        }

    def input(self, command: str):
        """
        :param command:
        :return:
        """
        # the trailing space is needed by the state machine to parse properly
        self.command = command.strip()
        self.char_list = list(self.command + ' ')
        self.state = State.START
        self.count = 0

    def token(self, word: str) -> tuple[Token, Union[str, int, float]]:
        """
        Check for matching patterns and return token code and data.
        Keywords are always checked first.
        The order patterns are checked matters.
        :param word:
        :return: tuple containing the toekn and its value
        """
        if word in self.keywords:
            tup = self.keywords[word], word
        elif re.search(UID_PATTERN, word):
            tup = Token.UID, word
        elif re.search(LONG_DATE_PATTERN, word) \
                or re.search(SHORT_DATE_PATTERN, word) \
                or re.search(MONTH_YEAR_PATTERN, word):
            tup = Token.VALUE, word
        elif re.search(FLOAT_PATTERN, word):
            tup = Token.VALUE, float(word)
        elif re.search(INT_PATTERN, word):
            tup = Token.VALUE, int(word)
        elif re.search(FILE_PATTERN, word):
            tup = Token.FILE, word
        elif re.search(NAME_PATTERN, word):
            tup = Token.NAME, word
        else:
            tup = Token.INVALID, word
        return tup

    def next_token(self) -> tuple[Token, Union[str, int, float]]:
        """
        Return the next token in the input stream
        :return: tuple containing the token and value
        """
        word = ''
        while self.count < len(self.char_list):
            c = self.char_list[self.count]
            self.count += 1
            assert isinstance(c, str)
            if self.state == State.START:
                if c.isspace():
                    pass
                elif c in STRING_DELIMITERS:
                    self.state = State.STRING  # start of string
                    word = ''
                else:
                    word = c
                    self.state = State.WORD  # start of word
            elif self.state == State.WORD:
                if c.isspace():
                    self.state = State.START
                    return self.token(word)  # end of word
                else:
                    word += c
            elif self.state == State.STRING:
                if c in STRING_DELIMITERS:
                    self.state = State.START
                    return Token.STRING, word  # end of string
                else:
                    word += c

        # Check for unterminated string
        if self.state == State.STRING:
            return Token.INVALID, f'{UNTERMINATED_STRING} [{word[0:10]}...]'
        else:
            return Token.EOS, ''


if __name__ == '__main__':
    lx = Lexer()
    lx.input('item "this is a string list 20/10/2022 07/24 3.4 7 +')
    while True:
        t, v = lx.next_token()
        print(t, v)
        if t in [Token.EOS, Token.INVALID]:
            break
