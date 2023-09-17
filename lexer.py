import re
from enum import Enum, auto


# Token identifiers
class Tid(Enum):
    # commands
    ITEM = auto()
    FIELD = auto()
    TAG = auto()
    ADD = auto()
    CREATE = auto()
    READ = auto()
    WRITE = auto()
    EXPORT = auto()
    DUMP = auto()
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
    REPORT = auto()
    EOS = auto()
    # switches
    SW_SENSITIVE = auto()
    SW_NAME = auto()
    SW_FIELD_NAME = auto()
    SW_FIELD_VALUE = auto()
    SW_TAG = auto()
    SW_NOTE = auto()
    # error
    INVALID = auto()


# Lexer DFA states
class State(Enum):
    START = auto()
    WORD = auto()
    STRING = auto()


# Token classes
LEX_ACTIONS = [Tid.ITEM, Tid.FIELD, Tid.TAG]
LEX_DATABASE = [Tid.CREATE, Tid.READ, Tid.WRITE, Tid.EXPORT, Tid.DUMP]
LEX_SUBCOMMANDS = [Tid.LIST, Tid.PRINT, Tid.DUMP, Tid.SEARCH, Tid.COUNT,
                   Tid.ADD, Tid.RENAME, Tid.DELETE, Tid.EDIT]
LEX_MISC = [Tid.REPORT]
LEX_STRINGS = [Tid.NAME, Tid.STRING]

# Regular expressions
LONG_DATE_PATTERN = r'\d\d/\d\d/\d\d\d\d'
SHORT_DATE_PATTERN = r'\d\d/\d\d/\d\d'
MONTH_YEAR_PATTERN = r'\d\d/\d\d'
FILE_PATTERN = r'[a-z0-9]+\.[a-z0-9]+'
NAME_PATTERN = r'[a-zA-Z_][a-zA-Z_0-9]*'
INT_PATTERN = r'\d+'
FLOAT_PATTERN = r'\d*\.\d+'

# Valid string delimiters
STRING_DELIMITERS = ['\'', '"']

# Unterminated string error message
UNTERMINATED_STRING = 'unterminated'


class Token:
    """
    Tokens are objects that have an id and value
    """

    def __init__(self, tid: Tid, value: int | float | str):
        self._tid = tid
        self._value = value
        pass

    def __eq__(self, token):
        if isinstance(token, Token):
            return self.tid == token.tid and self.value == token.value
        return False

    def __str__(self):
        return f'({self._tid}, {self._value})'

    @property
    def tid(self):
        return self._tid

    @property
    def value(self):
        return self._value


class Lexer:

    def __init__(self):
        self.command = ''
        self.count = 0
        self.char_list = []
        self.state = State.START
        self.keywords = {
            'item': Tid.ITEM, 'field': Tid.FIELD, 'tag': Tid.TAG,
            'create': Tid.CREATE, 'read': Tid.READ, 'write': Tid.WRITE,
            'export': Tid.EXPORT, 'print': Tid.PRINT, 'dump': Tid.DUMP,
            'list': Tid.LIST, 'count': Tid.COUNT, 'search': Tid.SEARCH,
            'add': Tid.ADD, 'rename': Tid.RENAME, 'delete': Tid.DELETE, 'edit': Tid.EDIT,
            'report': Tid.REPORT,
            # aliases
            'save': Tid.WRITE, 'ren': Tid.RENAME, 'del': Tid.DELETE
        }
        self.switches = {
            '-s': Tid.SW_SENSITIVE,
            '-n': Tid.SW_NAME,
            '-t': Tid.SW_TAG,
            '-fn': Tid.SW_FIELD_NAME,
            '-fv': Tid.SW_FIELD_VALUE,
            '-no': Tid.SW_NOTE
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

    def token(self, word: str) -> Token:
        """
        Check for matching patterns and return token code and data.
        Keywords are always checked first.
        The order patterns are checked matters.
        :param word:
        :return: TODO
        """
        if word in self.keywords:
            tup = Token(self.keywords[word], word)
        elif word in self.switches:
            tup = Token(self.switches[word], True)
        elif re.search(LONG_DATE_PATTERN, word) \
                or re.search(SHORT_DATE_PATTERN, word) \
                or re.search(MONTH_YEAR_PATTERN, word):
            tup = Token(Tid.VALUE, word)
        elif re.search(FLOAT_PATTERN, word):
            tup = Token(Tid.VALUE, float(word))
        elif re.search(INT_PATTERN, word):
            tup = Token(Tid.VALUE, int(word))
        elif re.search(FILE_PATTERN, word):
            tup = Token(Tid.FILE, word)
        elif re.search(NAME_PATTERN, word):
            tup = Token(Tid.NAME, word)
        else:
            tup = Token(Tid.INVALID, word)
        return tup

    def next_token(self) -> Token:
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
                    return Token(Tid.STRING, word)  # end of string
                else:
                    word += c

        # Check for unterminated string
        if self.state == State.STRING:
            return Token(Tid.INVALID, f'{UNTERMINATED_STRING} [{word[0:10]}...]')
        else:
            return Token(Tid.EOS, '')


if __name__ == '__main__':
    lx = Lexer()
    lx.input('item name "this is a string" list 20/10/2022 07/24 3.4 7 -s -n -t -fn -fv -no')
    while True:
        tok = lx.next_token()
        print(tok)
        if tok.tid in [Tid.EOS, Tid.INVALID]:
            break
