import pytest
from testing import random_bool, random_int, random_string, random_value, random_string_list, random_list_element
from testing import random_item, random_field_list
from items import ItemCollection, Item, Field
from items import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_SENSITIVE_KEY


def test_field():
    f = Field('name', 'abc', False)
    assert isinstance(f, Field)
    f = Field('name', 2, False)
    assert isinstance(f, Field)
    f = Field(random_string(), random_value(), random_bool())
    assert isinstance(f, Field)


def test_field_to_dict():
    d = Field('field_1', 'abc', False).to_dict()
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_1'
    assert d[FIELD_VALUE_KEY] == 'abc'
    assert d[FIELD_SENSITIVE_KEY] is False

    d = Field('field_2', 100, True).to_dict()
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_2'
    assert d[FIELD_VALUE_KEY] == 100
    assert d[FIELD_SENSITIVE_KEY] is True


def test_item():
    it = Item(random_string(), random_string_list(), random_string(), random_int(), random_field_list())
    assert isinstance(it, Item)


def test_add_item():
    ic = ItemCollection()
    ic.add(random_item())
    ic.add(random_item())
    ic.add(random_item())
    assert ic.count() == 3
    for key in ic.keys():
        assert key in ic


def test_add_duplicate_item():
    ic = ItemCollection()
    it = random_item()
    ic.add(it)
    with pytest.raises(KeyError):
        ic.add(it)


def test_get_item():
    ic = ItemCollection()
    ic.add(random_item())
    ic.add(random_item())
    ic.add(random_item())
    for key in ic.keys():
        assert isinstance(ic.get(key), Item)


def test_get_not_existent_item():
    ic = ItemCollection()
    with pytest.raises(KeyError):
        _ = ic.get('some_key')


def test_remove_item():
    ic = ItemCollection()
    ic.add(random_item())
    ic.add(random_item())
    ic.add(random_item())
    key = random_list_element(ic.keys())
    ic.remove(key)
    assert ic.count() == 2
    assert key not in ic


def test_remove_not_existent_item():
    ic = ItemCollection()
    with pytest.raises(KeyError):
        _ = ic.remove('some_key')
