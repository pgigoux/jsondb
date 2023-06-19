import pytest
from tables import Table, FieldTable, TagTable


def test_table():
    # Create table
    tt = Table()
    assert isinstance(tt, Table)

    # Add elements
    tt.add(name='one')
    tt.add(name='two', uid='2000')
    tt.add(name='three', uid='3000')
    tt.add(name='four', uid='4000', value=4)

    # Test count
    assert tt.count() == 4

    # Add duplicates
    with pytest.raises(KeyError):
        tt.add(name='one')
        tt.add(uid='2000')

    # Test has_name and has_uid
    assert tt.has_name('one') is True
    assert tt.has_name('two') is True
    assert tt.has_name('three') is True
    assert tt.has_name('four') is True
    assert tt.has_name('ten') is False
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
    tt.remove(uid='2000')
    assert tt.count() == 3
    assert tt.has_uid('2000') is False
    assert tt.has_name('two') is False
    assert tt.has_name('one') is True
    assert tt.has_name('three') is True
    assert tt.has_uid('3000') is True
    assert tt.has_name('four') is True
    assert tt.has_uid('4000') is True

    # Remove non existent elements
    with pytest.raises(KeyError):
        tt.remove(name='five')
        tt.remove(uid='5000')

    # Rename existent element
    tt.rename('three', 'zero')
    assert tt.has_name('three') is False
    assert tt.has_name('zero') is True
    assert tt.get_uid('zero') == '3000'

    # Rename non existent element
    with pytest.raises(KeyError):
        tt.rename('five', 'six')

    assert tt.get_attributes(name='four') == {'value': 4}
    assert tt.get_attributes(uid='4000') == {'value': 4}
