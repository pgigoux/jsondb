# Starting values for the different uid
FIRST_TAG_TABLE_UID = 10
FIRST_FIELD_TABLE_UID = 100
FIRST_FIELD_UID = 5000
FIRST_ITEM_UID = 1000


class _Uid:
    """
    Generic class used to generate unique sequential identifiers
    These identifiers are shorter than the ones generated by uuid4()
    """

    # uid counter
    uid_next = 0

    # List of all uid returned. Used to check for duplicates.
    uid_list = []

    @classmethod
    def clear(cls):
        """
        Clear all class variables
        :return:
        """
        cls.uid_next = 0
        cls.uid_list = []

    @classmethod
    def reset(cls, value):
        """
        Reset the uid counter
        """
        cls.uid_next = value

    @classmethod
    def add_uid(cls, uid: int):
        """
        Add unique identifier
        :param uid:
        :raise: ValueError if the uid is already in use
        """
        if uid not in cls.uid_list:
            cls.uid_list.append(uid)
            cls.uid_next = max(cls.uid_next, uid + 1)
        else:
            raise ValueError('duplicate uid')

    @classmethod
    def get_uid(cls) -> int:
        """
        Generate unique identifier
        :return uid
        :raise: ValueError if the uid is already in use
        """
        uid = cls.uid_next
        if uid not in cls.uid_list:
            cls.uid_list.append(uid)
        else:
            raise ValueError('duplicate uid')
        cls.uid_next += 1
        return uid

    @classmethod
    def dump(cls, title=''):
        title = 'uid dump' if not title else title
        print(f'{title}:')
        print(f'\tnext  {cls.uid_next}')
        print(f'\tlen   {len(cls.uid_list)}')
        print(f'\tlist  {cls.uid_list[0:10]}')


class TagTableUid(_Uid):
    """
    Subclass for the tag table
    """
    uid_next = FIRST_TAG_TABLE_UID
    uid_list = []


class FieldTableUid(_Uid):
    """
    Subclass for the field table
    """
    uid_next = FIRST_FIELD_TABLE_UID
    uid_list = []


class FieldUid(_Uid):
    """
    Subclass for the field collection
    """
    uid_next = FIRST_FIELD_UID
    uid_list = []


class ItemUid(_Uid):
    """
    Subclass for the item collection
    """
    uid_next = FIRST_ITEM_UID
    uid_list = []


if __name__ == '__main__':
    pass