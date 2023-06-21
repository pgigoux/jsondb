from utils import get_uid
from common import KEY_NAME, KEY_UID, FIELD_SENSITIVE_KEY

# List of standard table keys. Used to exclude keys from the user defined attributes
TABLE_KEY_LIST = [KEY_NAME, KEY_UID]


class Table:

    def __init__(self, table_name=''):
        """
        The table information is stored in three dictionaries
        name_dict provides the mapping between names and their unique identifiers
        uid_dict provides the mapping between unique identifiers and names
        attr_dict is used to store attributes other than the name (indexed by unique identifier)
        """
        self.table_name = table_name
        self.name_dict = {}
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

    def has_uid(self, uid):
        """
        Determine whether a uid is already in the table
        :param uid: element uid
        :return: True if it does, False otherwise
        """
        return uid in self.uid_dict

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

        # The unique identifier is optional. Assign default if not present.
        uid = ''
        if KEY_UID in kwargs:
            uid = str(kwargs[KEY_UID])
        if not uid:
            uid = get_uid()

        # Enter additional elements to the table
        if name not in self.name_dict:
            self.name_dict[name] = uid
            self.uid_dict[uid] = name
            self.attr_dict[uid] = {x: kwargs[x] for x in kwargs if x not in TABLE_KEY_LIST}
        else:
            raise KeyError(f'{name} already exists')

    def remove(self, name='', uid=''):
        """
        Remove by name or unique identifier
        :param name:
        :param uid:
        :raise: KeyError if the name is not found
        """
        if name:
            uid = self.name_dict[name]
        elif uid:
            name = self.uid_dict[uid]
        else:
            raise ValueError('must specify the name or the uid')
        del (self.name_dict[name])
        del (self.uid_dict[uid])
        del (self.attr_dict[uid])

    def rename(self, old_name: str, new_name: str):
        """
        Rename table element. The unique identifier does not change.
        :param old_name: old name
        :param new_name: new name
        :return:
        """
        if old_name in self.name_dict:
            self.name_dict[new_name] = self.name_dict[old_name]
            del (self.name_dict[old_name])
        else:
            raise KeyError('name not found')

    def get_uid(self, name: str) -> str:
        """
        Get the unique identifier from the name
        :param name: tag name
        :return: unique identifier
        :raise: IndexError if the tag does not exists
        """
        if name in self.name_dict:
            return self.name_dict[name]
        else:
            raise KeyError(f'name {name} not found')

    def get_name(self, uid: str) -> str:
        """
        Get the name from the unique identifier
        :param uid: unique identifier
        :return: element name
        :raise: KeyError if the tag does not exists
        """
        if uid in self.uid_dict:
            return self.uid_dict[uid]
        else:
            raise KeyError(f'uid {uid} not found in table')

    def get_attributes(self, name='', uid='') -> dict:
        """
        Get the additional attributes for a table entry either by name or uid
        :param name: name
        :param uid: unique identifier
        :return:
        """
        if name and name in self.name_dict:
            return self.attr_dict[self.name_dict[name]]
        elif uid and uid in self.uid_dict:
            return self.attr_dict[uid]
        else:
            raise KeyError(f'name={name} or uid={uid} not in the table')

    def to_dict(self) -> list:
        """
        Return table elements as a list of dictionaries where each element is the name,
        the unique identifier and the attributes.
        :return: list of elements
        """
        output_list = []
        for name in self.name_dict:
            uid = self.name_dict[name]
            d = {KEY_NAME: name, KEY_UID: uid}
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
            print(margin + f'\t{KEY_NAME}=\'{name}\', {KEY_UID}={uid}, attr={self.attr_dict[uid]}')


class TagTable(Table):

    def __init__(self):
        super().__init__('Tags')

    def add(self, tag_name: str, uid=''):
        super().add(name=tag_name, uid=uid)


class FieldTable(Table):

    def __init__(self):
        super().__init__('Fields')

    def add(self, name: str, sensitive=False, uid=''):
        super().add(name=name, uid=uid, sensitive=sensitive)

    def is_sensitive(self, name: str):
        return self.get_attributes(name=name)[FIELD_SENSITIVE_KEY]

    if __name__ == '__main__':
        t = Table()
        t.add(name='one', uid=1, sensitive=True, value='hello')
        t.add(name='two', value=6)
        t.dump()

        print(t.get_attributes(name='one'))
        print(t.get_attributes(name='two'))
        print(t.get_attributes(uid='1'))

        tg = TagTable()
        tg.add('abc')
        tg.add('cdf', uid='1234')
        tg.dump()

        ft = FieldTable()
        ft.add('password', sensitive=True, uid='6')
        ft.add('url')
        print('sensitive', ft.is_sensitive('password'))
        print(ft.to_dict())
        ft.dump()
