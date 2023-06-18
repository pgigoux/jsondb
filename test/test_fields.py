import pytest
from testing import random_bool, random_string, random_value, random_list_element, random_field
from items import FieldCollection, Field
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


def test_add_field():
    fc = FieldCollection()
    fc.add(random_field())
    fc.add(random_field())
    fc.add(random_field())
    assert fc.count() == 3
    for key in fc.keys():
        assert key in fc


def test_add_duplicate_field():
    fc = FieldCollection()
    f = random_field()
    fc.add(f)
    with pytest.raises(KeyError):
        fc.add(f)


def test_get_field():
    fc = FieldCollection()
    fc.add(random_field())
    fc.add(random_field())
    fc.add(random_field())
    for key in fc.keys():
        assert isinstance(fc.get(key), Field)


def test_get_not_existent_field():
    fc = FieldCollection()
    with pytest.raises(KeyError):
        _ = fc.get('some_key')


def test_remove_field():
    fc = FieldCollection()
    fc.add(random_field())
    fc.add(random_field())
    fc.add(random_field())
    key = random_list_element(fc.keys())
    fc.remove(key)
    assert fc.count() == 2
    assert key not in fc


def test_remove_not_existent_field():
    fc = FieldCollection()
    with pytest.raises(KeyError):
        _ = fc.remove('some_key')
