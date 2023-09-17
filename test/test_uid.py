import pytest
from uid import TagTableUid, FieldTableUid, FieldUid, ItemUid
from uid import FIRST_TAG_TABLE_UID, FIRST_FIELD_TABLE_UID, FIRST_FIELD_UID, FIRST_ITEM_UID


def test_tag_table_uid():

    TagTableUid.clear()
    TagTableUid.reset(FIRST_TAG_TABLE_UID)
    assert TagTableUid.get_uid() == FIRST_TAG_TABLE_UID

    uid_1 = TagTableUid.get_uid()
    assert isinstance(uid_1, int)

    uid_2 = TagTableUid.get_uid()
    assert isinstance(uid_2, int)

    assert uid_2 == uid_1 + 1

    # force a duplicate
    # TagTableUid.dump()
    with pytest.raises(ValueError):
        TagTableUid.reset(FIRST_TAG_TABLE_UID)
        _ = TagTableUid.get_uid()


def test_field_table_uid():

    FieldTableUid.clear()
    FieldTableUid.reset(FIRST_FIELD_TABLE_UID)
    assert FieldTableUid.get_uid() == FIRST_FIELD_TABLE_UID

    uid_1 = FieldTableUid.get_uid()
    assert isinstance(uid_1, int)

    uid_2 = FieldTableUid.get_uid()
    assert isinstance(uid_2, int)

    assert uid_2 == uid_1 + 1

    # force a duplicate
    # FieldTableUid.dump()
    with pytest.raises(ValueError):
        FieldTableUid.reset(FIRST_FIELD_TABLE_UID)
        _ = FieldTableUid.get_uid()


def test_field_uid():

    FieldUid.clear()
    FieldUid.reset(FIRST_FIELD_UID)
    assert FieldUid.get_uid() == FIRST_FIELD_UID

    uid_1 = FieldUid.get_uid()
    assert isinstance(uid_1, int)

    uid_2 = FieldUid.get_uid()
    assert isinstance(uid_2, int)

    assert uid_2 == uid_1 + 1

    # force a duplicate
    # FieldUid.dump()
    with pytest.raises(ValueError):
        FieldUid.reset(FIRST_FIELD_UID)
        _ = FieldUid.get_uid()


def test_item_uid():

    ItemUid.clear()
    ItemUid.reset(FIRST_ITEM_UID)
    assert ItemUid.get_uid() == FIRST_ITEM_UID

    uid_1 = ItemUid.get_uid()
    assert isinstance(uid_1, int)

    uid_2 = ItemUid.get_uid()
    assert isinstance(uid_2, int)

    assert uid_2 == uid_1 + 1

    # force a duplicate
    # ItemUid.dump()
    with pytest.raises(ValueError):
        ItemUid.reset(FIRST_ITEM_UID)
        _ = ItemUid.get_uid()


if __name__ == '__main__':
    test_tag_table_uid()
    test_field_table_uid()
    test_field_uid()
    test_item_uid()
