import pytest
from tables import Table, FieldTable, TagTable
from common import KEY_NAME, KEY_UID, KEY_COUNT, FIELD_SENSITIVE_KEY


def test_table():
    # Create table
    tt = Table()
    assert isinstance(tt, Table)

    # Add elements
    tt.add(name='one')
    tt.add(name='two', uid=2000, value=2)
    tt.add(name='three', uid=3000, value=3)
    tt.add(name='four', uid=4000, value=4)
    tt.add(name='five', uid=5000, value=5)
    # tt.dump()

    # Test number of elements
    assert len(tt) == 5

    # Add duplicates
    with pytest.raises(KeyError):
        tt.add(name='one')
        tt.add(uid=2000)

    # Test has_name and has_uid
    assert tt.has_name('one') is True
    assert tt.has_name('two') is True
    assert tt.has_name('three') is True
    assert tt.has_name('four') is True
    assert tt.has_name('five') is True
    assert tt.has_name('six') is False
    assert tt.has_uid(2000) is True
    assert tt.has_uid(3000) is True
    assert tt.has_uid(4000) is True
    assert tt.has_uid(5000) is True
    assert tt.has_uid(6000) is False

    # Test get_name and get_uid
    assert tt.get_name(2000) == 'two'
    assert tt.get_uid('two') == 2000
    assert tt.get_name(3000) == 'three'
    assert tt.get_uid('three') == 3000
    assert tt.get_name(4000) == 'four'
    assert tt.get_uid('four') == 4000
    assert tt.get_name(5000) == 'five'
    assert tt.get_uid('five') == 5000

    # Counters for existent elements
    tt.increment(name='one')
    tt.increment(name='two', n=2)
    tt.increment(uid=3000)
    assert tt.count(name='one') == 1
    assert tt.count(name='two') == 2
    assert tt.count(uid=3000) == 1
    assert tt.count(name='four') == 0
    assert tt.count(uid=5000) == 0

    # Counter for non-existent element
    with pytest.raises(KeyError):
        tt.increment(name='six')

    # Remove  elements with zero count
    tt.remove(uid=4000)
    tt.remove(name='five')
    assert len(tt) == 3
    assert tt.has_name('one') is True
    assert tt.has_name('two') is True
    assert tt.has_uid(2000) is True
    assert tt.has_name('three') is True
    assert tt.has_uid(3000) is True
    assert tt.has_name('four') is False
    assert tt.has_uid(4000) is False
    assert tt.has_name('five') is False
    assert tt.has_uid(5000) is False

    # Remove elements with non-zero count
    with pytest.raises(ValueError):
        tt.remove(name='one')
        tt.remove(uid=2000)
        tt.remove(name='three')

    # Remove non existent elements
    with pytest.raises(KeyError):
        tt.remove(name='unknown')
        tt.remove(uid=10000)

    # Rename existent element
    tt.rename('three', 'zero')
    assert tt.has_name('three') is False
    assert tt.has_uid(3000) is True
    assert tt.has_name('zero') is True
    assert tt.get_uid('zero') == 3000

    # Rename non existent element
    with pytest.raises(KeyError):
        tt.rename('ten', 'six')

    # Rename to existent element
    with pytest.raises(KeyError):
        tt.rename('one', 'zero')
        tt.rename('zero', 'one')
        tt.rename('three', 'one')
        tt.rename('two', 'zero')
        tt.rename('two', 'three')

    # Attributes
    assert tt.get_attributes(2000) == {'value': 2}
    assert tt.get_attributes(3000) == {'value': 3}


def test_tag_table():
    tt = TagTable()
    assert isinstance(tt, TagTable)

    tt.add('one', uid='1000')
    tt.add('two', uid='2000')
    tt.increment(name='one')

    assert tt.export() == [{KEY_NAME: 'one', KEY_UID: 1000},
                           {KEY_NAME: 'two', KEY_UID: 2000}]


def test_field_table():
    ft = FieldTable()
    assert isinstance(ft, FieldTable)

    ft.add('one', sensitive=True, uid='1000')
    ft.add('two', uid=2000)
    ft.increment(name='one')

    assert ft.is_sensitive(1000) is True
    assert ft.is_sensitive(2000) is False

    assert ft.export() == [{KEY_NAME: 'one', KEY_UID: 1000, FIELD_SENSITIVE_KEY: True},
                           {KEY_NAME: 'two', KEY_UID: 2000, FIELD_SENSITIVE_KEY: False}]


if __name__ == '__main__':
    test_table()
    test_tag_table()
    test_field_table()
