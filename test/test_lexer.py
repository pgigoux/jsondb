from lexer import Lexer, Token, UNTERMINATED_STRING


def test_keywords():
    lx = Lexer()

    assert lx.token('item') == (Token.ITEM, 'item')
    assert lx.token('field') == (Token.FIELD, 'field')
    assert lx.token('tag') == (Token.TAG, 'tag')

    assert lx.token('create') == (Token.CREATE, 'create')
    assert lx.token('read') == (Token.READ, 'read')
    assert lx.token('write') == (Token.WRITE, 'write')
    assert lx.token('export') == (Token.EXPORT, 'export')
    assert lx.token('save') == (Token.WRITE, 'save')

    assert lx.token('list') == (Token.LIST, 'list')
    assert lx.token('search') == (Token.SEARCH, 'search')
    assert lx.token('print') == (Token.PRINT, 'print')
    assert lx.token('count') == (Token.COUNT, 'count')
    assert lx.token('rename') == (Token.RENAME, 'rename')
    assert lx.token('delete') == (Token.DELETE, 'delete')
    assert lx.token('edit') == (Token.EDIT, 'edit')
    assert lx.token('ren') == (Token.RENAME, 'ren')
    assert lx.token('del') == (Token.DELETE, 'del')


def test_expressions():
    lx = Lexer()
    assert lx.token('3.15') == (Token.VALUE, 3.15)
    assert lx.token('10') == (Token.VALUE, 10)
    assert lx.token('10/10/2020') == (Token.VALUE, '10/10/2020')
    assert lx.token('10/11') == (Token.VALUE, '10/11')
    assert lx.token('file.txt') == (Token.FILE, 'file.txt')
    assert lx.token('word') == (Token.NAME, 'word')
    assert lx.token('()') == (Token.INVALID, '()')


def test_strings():
    lx = Lexer()

    lx.input('"this is a string"')
    assert lx.next_token() == (Token.STRING, 'this is a string')

    lx.input("'this is another string'")
    assert lx.next_token() == (Token.STRING, 'this is another string')

    lx.input("'this is an unterminated string")
    t, v = lx.next_token()
    assert t == Token.INVALID and v.find(UNTERMINATED_STRING) == 0

    lx.input("'this is another unterminated string")
    assert t == Token.INVALID and v.find(UNTERMINATED_STRING) == 0


def test_next():
    lx = Lexer()

    lx.input('item search name 8 "one string" joe')
    assert lx.next_token() == (Token.ITEM, 'item')
    assert lx.next_token() == (Token.SEARCH, 'search')
    assert lx.next_token() == (Token.NAME, 'name')
    assert lx.next_token() == (Token.VALUE, 8)
    assert lx.next_token() == (Token.STRING, 'one string')
    assert lx.next_token() == (Token.NAME, 'joe')
    assert lx.next_token() == (Token.EOS, '')

    lx.input('field list "some unterminated string 8')
    assert lx.next_token() == (Token.FIELD, 'field')
    assert lx.next_token() == (Token.LIST, 'list')
    t, v = lx.next_token()
    assert t == Token.INVALID and v.find(UNTERMINATED_STRING) == 0


if __name__ == '__main__':
    test_keywords()
