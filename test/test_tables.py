import pytest
from tables import Table, FieldTable, TagTable


def test_table():
    # Create table
    tt = Table()
    assert isinstance(tt, Table)

    # Add elements
    tt.add(name='one')
    tt.add(name='two', uid='2000')
    tt.add(name='three', uid='3000', value=3)
    tt.add(name='four', uid='4000', value=4)

    # Test number of elements
    assert len(tt) == 4

    # Add duplicates
    with pytest.raises(KeyError):
        tt.add(name='one')
        tt.add(uid='2000')

    # Test has_name and has_uid
    assert tt.has_name('one') is True
    assert tt.has_name('two') is True
    assert tt.has_name('three') is True
    assert tt.has_name('four') is True
    assert tt.has_name('five') is False
    assert tt.has_uid('2000') is True
    assert tt.has_uid('3000') is True
    assert tt.has_uid('4000') is True
    assert tt.has_uid('5000') is False

    # Test get_name and get_uid
    assert tt.get_name('2000') == 'two'
    assert tt.get_uid('two') == '2000'
    assert tt.get_name('3000') == 'three'
    assert tt.get_uid('three') == '3000'

    # Remove existent element
    tt.remove('2000')
    assert len(tt) == 3
    assert tt.has_uid('2000') is False
    assert tt.has_name('two') is False
    assert tt.has_name('one') is True
    assert tt.has_name('three') is True
    assert tt.has_uid('3000') is True
    assert tt.has_name('four') is True
    assert tt.has_uid('4000') is True

    # Remove non existent elements
    with pytest.raises(KeyError):
        tt.remove('0000')
        tt.remove('5000')

    # Rename existent element
    tt.rename('three', 'zero')
    assert tt.has_name('three') is False
    assert tt.has_name('zero') is True
    assert tt.get_uid('zero') == '3000'

    # Rename non existent element
    with pytest.raises(KeyError):
        tt.rename('five', 'six')

    # Rename to existent element
    with pytest.raises(KeyError):
        tt.rename('one', 'four')
        tt.rename('one', 'zero')
        tt.rename('zero', 'one')
        tt.rename('zero', 'four')
        tt.rename('four', 'one')
        tt.rename('four', 'zero')

    # Attributes
    assert tt.get_attributes('3000') == {'value': 3}
    assert tt.get_attributes('4000') == {'value': 4}

    # Counters
    tt.increment(uid='3000', n=3)
    assert tt.count(uid='3000') == 3
    tt.increment(name='four')
    assert tt.count(name='four') == 1
    with pytest.raises(KeyError):
        tt.increment(uid='2000')
        _ = tt.count(uid='2000')


def test_tag_table():
    tt = TagTable()
    assert isinstance(tt, TagTable)

    tt.add('one', uid='1000')
    tt.add('two', uid='2000')

    assert tt.export() == [{'name': 'one', 'uid': '1000'}, {'name': 'two', 'uid': '2000'}]


def test_field_table():
    tt = FieldTable()
    assert isinstance(tt, FieldTable)

    tt.add('one', sensitive=True, uid='1000')
    tt.add('two', uid='2000')

    assert tt.is_sensitive('1000') is True
    assert tt.is_sensitive('2000') is False

    assert tt.export() == [{'name': 'one', 'uid': '1000', 'sensitive': True},
                           {'name': 'two', 'uid': '2000', 'sensitive': False}]
