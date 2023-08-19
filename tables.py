from typing import Optional
from utils import Uid
from common import KEY_NAME, KEY_UID, KEY_COUNT, FIELD_SENSITIVE_KEY

# List of standard table keys. Used to exclude keys from the user defined attributes
TABLE_KEY_LIST = [KEY_NAME, KEY_UID, KEY_COUNT]


class Table:

    def __init__(self, table_name=''):
        """
        The table class is used to provide a mapping between names and unique identifiers.
        I can also store additional attributes and also a counter for each unique identifier.
        The table information is stored in four dictionaries:
        name_dict: provides the unique identifier for a given name (indexed by name)
        uid_dict: provides the name for a given unique identifier (indexed by unique identifier)
        count_dict: keeps track how many elements of each type are present (indexed by unique identifier)
        attr_dict: Stores additional attributes other than the name and count (indexed by unique identifier)
        """
        self.table_name = table_name
        self.name_dict = {}
        self.count_dict = {}
        self.uid_dict = {}
        self.attr_dict = {}

    def __len__(self):
        return len(self.name_dict)

    def has_name(self, name):
        """
        Determine whether a name is already in the table
        :param name: element name
        :return: True if it does, False otherwise
        """
        return name in self.name_dict

    def has_uid(self, uid: int):
        """
        Determine whether a uid is already in the table
        :param uid: element uid
        :return: True if it does, False otherwise
        """
        return uid in self.uid_dict

    def get_uid(self, name: str) -> int:
        """
        Get the unique identifier from the name
        :param name: tag name
        :return: unique identifier
        :raise: IndexError if the tag does not exists
        """
        if name in self.name_dict:
            return self.name_dict[name]
        else:
            raise KeyError(f'name {name} not in the table')

    def get_name(self, uid: int) -> str:
        """
        Get the name from the unique identifier
        :param uid: unique identifier
        :return: element name
        :raise: KeyError if the tag does not exists
        """
        if uid in self.uid_dict:
            return self.uid_dict[uid]
        else:
            raise KeyError(f'uid {uid} not in table')

    def add(self, **kwargs):
        """
        Add a new element to the table.
        :param kwargs: arguments
        :raise: KeyError if the tag already exists
        """
        # A name must be specified
        if KEY_NAME in kwargs:
            name = kwargs[KEY_NAME]
        else:
            raise KeyError('no name specified')

        # Enter elements to the table
        if name not in self.name_dict:

            # The unique identifier is optional.
            # Generate one if not present and make sure it's of the right type.
            uid = None
            if KEY_UID in kwargs:
                uid = kwargs[KEY_UID]
            if uid is None:
                uid = Uid.get_uid()
            else:
                uid = int(uid)

            # Update table
            self.name_dict[name] = uid
            self.uid_dict[uid] = name
            self.count_dict[uid] = 0
            self.attr_dict[uid] = {x: kwargs[x] for x in kwargs if x not in TABLE_KEY_LIST}

        else:
            raise KeyError(f'{name} already exists')

    def remove(self, name='', uid: Optional[int] = None):
        """
        Remove item from the table
        :param name: name
        :param uid: unique identifier
        :raise: KeyError if the uid is not found
        """
        if name and name in self.name_dict:
            uid = self.name_dict[name]
        if uid is not None and uid in self.uid_dict:
            name = self.uid_dict[uid]
            if self.count(uid=uid) == 0:
                del (self.name_dict[name])
                del (self.uid_dict[uid])
                del (self.count_dict[uid])
                del (self.attr_dict[uid])
            else:
                raise ValueError(f'count is not zero')
        else:
            raise KeyError(f'{uid} not in the table')

    def rename(self, old_name: str, new_name: str):
        """
        Rename table element. The unique identifier does not change.
        :param old_name: old name
        :param new_name: new name
        :return:
        """
        if old_name in self.name_dict:
            if new_name not in self.name_dict:
                self.name_dict[new_name] = self.name_dict[old_name]
                del (self.name_dict[old_name])
            else:
                raise KeyError(f'{new_name} already exists in table')
        else:
            raise KeyError(f'{old_name} not in the table')

    def count(self, name='', uid: Optional[int] = None) -> int:
        """
        Return the element count
        The table element can be referenced by name or uid
        :param name: name
        :param uid: unique identifier
        :return: element count
        """
        if name and name in self.name_dict:
            uid = self.name_dict[name]
        if uid is not None and uid in self.uid_dict:
            return self.count_dict[uid]
        else:
            raise KeyError(f'uid {uid} not in the table')

    def increment(self, name='', uid: Optional[int] = None, n=1):
        """
        Increment the counter
        The table element can be referenced by name or uid
        :param name: name
        :param uid: unique identifier
        :param n: counter increment
        """
        if name and name in self.name_dict:
            uid = self.name_dict[name]
        if uid is not None and uid in self.uid_dict:
            self.count_dict[uid] += n
        else:
            raise KeyError(f'uid {uid} not in the table')

    def get_attributes(self, uid: int) -> dict:
        """
        Get the additional attributes for a table entry either by name or uid
        :param uid: unique identifier
        :raise: KeyError
        """
        if uid in self.uid_dict:
            return self.attr_dict[uid]
        else:
            raise KeyError(f'uid={uid} not in the table')

    def export(self) -> list:
        """
        Return table elements as a list of dictionaries where each element is the name,
        the unique identifier and the attributes.
        :return: list of elements
        """
        output_list = []
        for name in self.name_dict:
            uid = self.name_dict[name]
            d = {KEY_NAME: name, KEY_UID: uid, KEY_COUNT: self.count_dict[uid]}
            d.update(self.attr_dict[uid])
            output_list.append(d)
        return output_list

    def dump(self, indent=0):
        """
        Print all elements in the table. Used for debugging.
        The indent level allows for formatting the output
        :param indent: indent level
        """
        margin = '\t' * indent
        if self.table_name:
            print(margin + f'{self.table_name}:')
        else:
            print(margin + 'Table:')
        for name in self.name_dict:
            uid = self.name_dict[name]
            print(margin + f'\t{KEY_NAME}=\'{name}\', {KEY_UID}={uid}, count={self.count_dict[uid]}, '
                           f'attr={self.attr_dict[uid]}')


class TagTable(Table):

    def __init__(self):
        super().__init__('Tags')

    def add(self, tag_name: str, uid=None):
        """
        Add tag to table
        :param tag_name: tag name
        :param uid: unique identifier (optional)
        """
        super().add(name=tag_name, uid=uid)

    def next(self) -> tuple[str, str, int]:
        """
        Return next tag in the table
        :return: tuple with the tag uid, name and count
        """
        for name in sorted(self.name_dict):
            uid = self.name_dict[name]
            yield uid, name, self.count(uid=uid)


class FieldTable(Table):

    def __init__(self):
        super().__init__('Fields')

    def add(self, name: str, sensitive=False, uid=None):
        """
        Add field to the table
        :param name: field name
        :param sensitive: sensitive?
        :param uid: unique identifier
        """
        super().add(name=name, uid=uid, sensitive=sensitive)

    def is_sensitive(self, uid: int):
        """
        Check whether a field is sensitive
        :param uid: unique identifier
        :return: True if sensitive, False otherwise
        """
        return self.get_attributes(uid)[FIELD_SENSITIVE_KEY]

    def next(self) -> tuple[str, str, int, bool]:
        """
        Return next field in the table
        :return: tuple with the uid, name, count and sensitive flag
        """
        for name in sorted(self.name_dict):
            uid = self.name_dict[name]
            yield uid, name, self.count(uid=uid), self.get_attributes(uid)[FIELD_SENSITIVE_KEY]


if __name__ == '__main__':
    t = Table()
    t.add(name='one', uid=1, sensitive=True, value='hello')
    t.add(name='two', value=6)
    t.increment(name='one')
    t.dump()
    t.remove('one')
    t.remove(name='two')
    t.dump()
    exit(0)

    print('-' * 10)
    print(t.get_attributes(1))
    print(t.get_attributes(t.get_uid('two')))

    tg = TagTable()
    tg.add('abc')
    tg.add('cdf', uid=1234)
    tg.increment(name='abc', n=2)
    tg.dump()

    ft = FieldTable()
    ft.add('password', sensitive=True, uid='6')
    ft.add('url')
    print('sensitive', ft.is_sensitive(6))
    print(ft.export())
    ft.dump()

    print('--')
    for f_u, f_n, f_c, f_s in ft.next():
        print(f_u, f_n, f_c, f_s)

    print('--')
    for t_u, t_n, t_c, in tg.next():
        print(t_u, t_n, t_c)
