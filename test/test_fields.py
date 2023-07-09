import pytest
from crypt import Crypt
from testing import random_bool, random_string, random_int, random_value, random_list_element, random_field
from items import FieldCollection, Field
from items import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_SENSITIVE_KEY


def test_field():
    f = Field('name', 'abc', False)
    assert isinstance(f, Field)
    f = Field('name', 2, False)
    assert isinstance(f, Field)
    f = Field(random_string(), random_value(), random_bool())
    assert isinstance(f, Field)


def test_field_export():
    value = random_string()
    d = Field('field_1', value, False).export()
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_1'
    assert d[FIELD_VALUE_KEY] == value
    assert d[FIELD_SENSITIVE_KEY] is False

    value = random_int()
    d = Field('field_2', value, True).export()
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_2'
    assert d[FIELD_VALUE_KEY] == value
    assert d[FIELD_SENSITIVE_KEY] is True


def test_field_export_encryption():
    c = Crypt('test')
    value = random_string()
    encrypted_value = c.encrypt_str2str(value)

    # non-sensitive value
    d = Field('field_1', encrypted_value, False).export(crypt=c)
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_1'
    assert d[FIELD_VALUE_KEY] == encrypted_value
    assert d[FIELD_SENSITIVE_KEY] is False

    # sensitive value
    d = Field('field_2', encrypted_value, True).export(crypt=c)
    assert FIELD_NAME_KEY in d
    assert FIELD_VALUE_KEY in d
    assert FIELD_NAME_KEY in d
    assert d[FIELD_NAME_KEY] == 'field_2'
    assert d[FIELD_VALUE_KEY] == value
    assert d[FIELD_SENSITIVE_KEY] is True


def test_add_field():
    fc = FieldCollection()
    fc.add(random_field())
    fc.add(random_field())
    fc.add(random_field())
    assert len(fc) == 3
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
    assert len(fc) == 2
    assert key not in fc


def test_remove_not_existent_field():
    fc = FieldCollection()
    with pytest.raises(KeyError):
        _ = fc.remove('some_key')
