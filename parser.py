import ply.lex as lex
import ply.yacc as yacc

"""
----------------------------------------------------------------
Lexer definitions
----------------------------------------------------------------
"""

basic = (
    'UID',
    'DATE',
    'NUMBER',
    'FILENAME',
    'ID',
    'STRING',
    'EQUALS',
)

reserved = {
    # main commands
    'item': 'ITEM',
    'field': 'FIELD',
    'tag': 'TAG',
    'read': 'READ',
    'write': 'WRITE',
    'export': 'EXPORT',
    'quit': 'QUIT',
    # subcommands
    'list': 'LIST',
    'print': 'PRINT',
    'add': 'ADD',
    'del': 'DELETE',
    'edit': 'EDIT',
    'rename': 'RENAME',
    'count': 'COUNT',
    'search': 'SEARCH',
    # attributes
    'name': 'NAME',
    'value': 'VALUE'
}

tokens = basic + tuple(reserved.values())

t_ignore = ' \t'
t_EQUALS = r'='


def t_UID(t):
    r'[a-z0-9]*-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+'
    return t


def t_DATE(t):
    r'\d\d/\d\d/\d\d\d\d'
    return t


def t_FILENAME(t):
    r'[a-z0-9]+\.[a-z0-9]+'
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'\'.*\''
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# ----------------------------------------------------------------
# Top level commands
# ----------------------------------------------------------------


def p_command(p):
    """
    command : item_command
            | field_command
            | tag_command
            | db_command
    """
    pass


# ----------------------------------------------------------------
# Item commands
# ----------------------------------------------------------------


def p_item_command(p):
    """
    item_command : item_list
                 | item_count
                 | item_search
                 | item_print
                 | item_delete
    """
    pass


def p_item_list(p):
    """item_list : ITEM LIST"""
    print('item list')


def p_item_count(p):
    """
    item_count : ITEM COUNT
    """
    print('item count')


def p_item_search(p):
    """
    item_search : ITEM SEARCH ID
    """
    print('item search', p[3])


def p_item_print(p):
    """
    item_print : ITEM PRINT UID
               | ITEM PRINT NUMBER
    """
    print('item print', p[3])


def p_item_delete(p):
    """
    item_delete : ITEM DELETE ID
    """
    print('item delete', p[3])


# ----------------------------------------------------------------
# Field commands
# ----------------------------------------------------------------


def p_field_command(p):
    """
    field_command : FIELD
    """
    pass


# ----------------------------------------------------------------
# Tag commands
# ----------------------------------------------------------------


def p_tag_command(p):
    """
    tag_command : TAG
    """
    pass


# ----------------------------------------------------------------
# Database commands
# ----------------------------------------------------------------

def p_db_commands(p):
    """
    db_command : db_read
               | db_write
               | db_export
    """
    pass


def p_db_read(p):
    """
    db_read : READ
            | READ FILENAME 
    """
    print('db_read', p[2])


def p_db_write(p):
    """
    db_write : WRITE
    """
    print('db_write')


def p_db_export(p):
    """
    db_export : EXPORT FILENAME
    """
    print('db_export', p[2])


def p_db_quit(p):
    """
    db_quit : QUIT
    """
    print('db_quit')


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


def test_lexer():
    test_lex = lex.lex()
    data = "file.txt 95781623-fc0e-4ab0-a57c-dd286c5ae1c8 15/10/2023 name john 34 value '67 stars' item"
    test_lex.input(data)

    # Tokenize
    while True:
        tok = test_lex.token()
        if not tok:
            break  # No more input
        print(tok)


if __name__ == '__main__':
    lexer = lex.lex()
    parser = yacc.yacc()
    while True:
        try:
            command = input('db> ')
        except EOFError:
            break
        if len(command.strip()) > 0:
            parser.parse(command)
