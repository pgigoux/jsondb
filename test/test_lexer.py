from lexer import Lexer, Token


def test_keywords():
    lx = Lexer()
    assert lx.token('item') == (Token.ITEM, 'item')
    assert lx.token('field') == (Token.FIELD, 'field')
    assert lx.token('tag') == (Token.TAG, 'tag')
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
    for t in lx.next():
        assert t == (Token.STRING, 'this is a string')

    lx.input("'this is another string'")
    for t in lx.next():
        assert t == (Token.STRING, 'this is another string')

    lx.input('"this is a string')
    for t in lx.next():
        assert t == (Token.UNTERMINATED, '')

    lx.input("'this is another string")
    for t in lx.next():
        assert t == (Token.UNTERMINATED, '')


def test_next():
    lx = Lexer()

    lx.input('item search name 8 "one string" joe')
    out = []
    for t in lx.next():
        out.append(t)
    assert out == [(Token.ITEM, 'item'),
                   (Token.SEARCH, 'search'),
                   (Token.NAME, 'name'),
                   (Token.VALUE, 8),
                   (Token.STRING, 'one string'),
                   (Token.NAME, 'joe')]

    lx.input('field list "unterminated string 8')
    out = []
    for t in lx.next():
        out.append(t)
    assert out == [(Token.FIELD, 'field'), (Token.LIST, 'list'), (Token.UNTERMINATED, '')]
