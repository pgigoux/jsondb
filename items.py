from abc import ABC, abstractmethod
from typing import Generator, Optional, Union
from crypt import Crypt
from utils import Uid, filter_control_characters
from common import FIELD_NAME_KEY, FIELD_VALUE_KEY, FIELD_UID_KEY, FIELD_SENSITIVE_KEY
from common import ITEM_NAME_KEY, ITEM_TAG_LIST_KEY, ITEM_NOTE_KEY, ITEM_TIMESTAMP_KEY, ITEM_UID_KEY, ITEM_FIELDS_KEY


class Element(ABC):
    """
    Generic element used to define Items and Fields
    """

    @abstractmethod
    def __str__(self):
        """
        Return string representation of the element
        :return:
        """
        pass

    @abstractmethod
    def get_id(self):
        """
        Return the element unique identifier
        :return:
        """
        pass

    @abstractmethod
    def export(self):
        """
        Export the element as a dictionary or list
        :return:
        """
        pass

    @abstractmethod
    def dump(self):
        """
        Print the element in a human readable format
        :return:
        """
        pass


class Collection:
    """
    Generic collection of objects used to define ItemCollection and FieldCollection
    """

    def __init__(self):
        self.data = {}

    def __contains__(self, key: str):
        return key in self.data

    def __len__(self) -> int:
        """
        Return the number of items in the collection
        :return: number of items
        """
        return len(self.data)

    def keys(self) -> list:
        """
        Return the list unique identifiers for the items in the collection
        :return:
        """
        return list(self.data.keys())

    def get(self, key) -> Element:
        """
        Get element corresponding to a given key
        :param key: element key
        :return:
        """
        if key in self.data:
            return self.data[key]
        else:
            raise KeyError(f'{key} does not exist')

    def sort_key(self, key: str):
        """
        Function called by next() to sort the keys
        It should be redefined in the subclasses
        :param key:
        :return: string used to sort
        """
        return ''

    def next(self) -> Generator[Element, None, None]:
        """
        Iterate over all elements in the collection
        The elements are sorted by name
        :return: next element
        """
        sorted_keys = sorted(self.keys(), key=self.sort_key)
        for key in sorted_keys:
            yield self.data[key]

    def add(self, element: Element):
        """
        Add element to the collection
        :param element: Item to add
        :raise: KeyError if the item already exists
        """
        key = element.get_id()
        if key not in self.data:
            self.data[key] = element
        else:
            raise KeyError(f'{key} already exists')

    def remove(self, key: str):
        """
        Remove item identified by a unique identifier
        :param key:
        :return:
        """
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError(f'{key} does not exist')

    def update(self, element: Element):
        """
        Update the collection with a new instance of an item
        :param element: element to update
        :raise: KeyError if the element is not in the collection already
        """
        key = element.get_id()
        if key in self.data:
            self.data[key] = Item
        else:
            raise KeyError(f'{key} does not exist')


class Field(Element):

    def __init__(self, name: str, value: str | int, sensitive=False):
        """
        Create a field
        :param name: field name
        :param value: field value
        :param sensitive: does the field contain sensitive information?
        """
        self.name = name
        self.value = value
        self.sensitive = sensitive
        self.uid = Uid.get_uid()

    def __str__(self):
        """
        :return: string representation of the field
        """
        return f'uid={self.uid}, name={self.name}, value={self.value}, sensitive={self.sensitive}'

    def get_name(self) -> str:
        return self.name

    def get_value(self) -> Union[str, int, float]:
        return self.value

    def get_sensitive(self) -> bool:
        return self.sensitive

    def get_id(self) -> int:
        """
        Return the field unique identifier
        :return: unique identifier
        """
        return self.uid

    def export(self, crypt: Optional[Crypt] = None) -> dict:
        """
        Convert field into a dictionary
        Sensitive values are returned in plain text in a decryption key is provided.
        :param crypt: decryption key (optional)
        :return: dictionary with field elements (name, value, sensitive flag)
        """
        if self.sensitive and crypt is not None:
            value = crypt.decrypt_str2str(self.value)
        else:
            value = self.value
        return {FIELD_NAME_KEY: self.name, FIELD_VALUE_KEY: value,
                FIELD_SENSITIVE_KEY: self.sensitive, FIELD_UID_KEY: str(self.uid)}

    def dump(self, indent=0):
        """
        Print the field in a human readable for. Used for debugging
        :param indent: indentation level for formatting
        """
        s = '\t' * indent + f'Field: name={self.name}, value={self.value}, sensitive={self.sensitive}, uid={self.uid}'
        print(s)


class FieldCollection(Collection):

    def sort_key(self, key: str):
        """
        Auxiliary routine called by next() to sort the field keys by field name
        :param key: key
        :return: field name for that key
        """
        field = self.get(key)
        assert isinstance(field, Field)
        return field.get_name()

    def export(self, crypt: Optional[Crypt] = None) -> dict:
        """
        Export the item collection as a dictionary
        Sensitive values are returned in plain text in a decryption key is provided.
        :param crypt: decryption key (optional)
        :return: dictionary representation
        """
        d = {}
        for key in self.data:
            field = self.data[key]
            assert isinstance(field, Field)
            d[key] = field.export(crypt)
        return d

    def dump(self, indent=0):
        """
        Dump collection contents in a human readable form
        :param indent: indentation level
        """
        print('Fields:')
        for key in self.data:
            self.data[key].dump(indent=indent + 1)


class Item(Element):
    def __init__(self, name: str, tag_list: list, note: str,
                 time_stamp: int, field_collection: FieldCollection):
        self.name = name
        self.tags = tag_list
        self.note = note
        self.time_stamp = time_stamp
        self.uid = Uid.get_uid()
        self.field_collection = field_collection

    def __str__(self):
        """
        :return: string representation of the item
        """
        field_list = [str(field) for field in self.field_collection.next()]
        return f'uid={self.uid}, name={self.name}, tags={self.tags}, note={self.note}, time={self.time_stamp}, ' + \
               f'fields={field_list}'

    def get_name(self) -> str:
        return self.name

    def get_tags(self) -> list:
        return self.tags

    def get_note(self) -> str:
        return self.note

    def get_timestamp(self):
        return self.time_stamp

    def get_id(self):
        """
        Return the item unique identifier
        :return: unique identifier
        """
        return self.uid

    def next_field(self) -> Generator[Field, None, None]:
        """
        Return the next field in an item
        :return: next field
        """
        for field in self.field_collection.next():
            yield field

    def export(self, crypt: Optional[Crypt] = None):
        """
        Export the item as a dictionary
        Sensitive values are returned in plain text in a decryption key is provided.
        :param crypt: decryption key (optional)
        :return: dictionary representation
        """
        return {ITEM_NAME_KEY: self.name,
                ITEM_TAG_LIST_KEY: self.tags,
                ITEM_NOTE_KEY: self.note,
                ITEM_TIMESTAMP_KEY: self.time_stamp,
                ITEM_UID_KEY: self.uid,
                ITEM_FIELDS_KEY: self.field_collection.export(crypt=crypt)
                }

    def dump(self, indent=0):
        """
        Dump item contents in a human readable form
        :param indent: indentation level
        """
        margin = '\t' * indent
        print(margin + 'Item')
        print(margin + f'\tname={self.name}, time={self.time_stamp}, uid={self.uid}')
        note = filter_control_characters(self.note)
        print(margin + f'\tnote={note}')
        print(margin + f'\ttags={self.tags}')
        for field in self.field_collection.next():
            assert isinstance(field, Field)
            field.dump(indent=indent + 1)


class ItemCollection(Collection):

    def sort_key(self, key: str):
        """
        Auxiliary routine called by next() to sort the item keys by item name
        :param key: key
        :return: item name for that key
        """
        item = self.get(key)
        assert isinstance(item, Item)
        return item.get_name()

    def export(self, crypt: Optional[Crypt] = None) -> dict:
        """
        Export the item collection as a dictionary
        Sensitive values are returned in plain text in a decryption key is provided.
        :param crypt: decryption key (optional)
        :return:
        """
        d = {}
        for item_uid in self.data:
            item = self.data[item_uid]
            assert isinstance(item, Item)
            d[item_uid] = item.export(crypt=crypt)
        return d

    def dump(self, indent=0):
        """
        Dump collection contents in a human readable form
        :param indent: indentation level
        """
        print('Items:')
        for uid in self.data:
            self.data[uid].dump(indent=indent + 1)


if __name__ == '__main__':
    fc1 = FieldCollection()
    fc1.add(Field('one', 1, True))
    fc1.add(Field('two', '2', False))

    fc2 = FieldCollection()
    fc2.add(Field('number', 1, True))
    fc2.add(Field('letter', 'b', False))
    fc2.add(Field('digit', '2', False))

    i1 = Item('one', ['a', 'b'], 'note 1', 12345, fc1)
    i2 = Item('two', ['c', 'd'], 'note 2', 3456, fc2)
    i3 = Item('three', ['e', 'f'], 'note 3', 68966, fc1)
    i4 = Item('four', ['e', 'f'], 'note 3', 16443, fc2)

    ic = ItemCollection()
    ic.add(i1)
    ic.add(i2)
    ic.add(i3)
    ic.add(i4)
    ic.dump()

    for it in ic.next():
        print(it)

    for f in fc2.next():
        print(f)

    exit(0)
