import pytest
from testing import random_int, random_string, random_string_list, random_list_element
from testing import random_item, random_field_list
from items import ItemCollection, Item


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
