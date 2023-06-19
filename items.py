from abc import ABC, abstractmethod
from typing import Generator
from utils import get_uid, filter_control_characters
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
    def to_dict(self):
        """
        Return a dictionary representation of the element
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

    def keys(self) -> list:
        """
        Return the list unique identifiers for the items in the collection
        :return:
        """
        return list(self.data.keys())

    def count(self) -> int:
        """
        Return the number of items in the collection
        :return: number of items
        """
        return len(self.data)

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

    def next(self) -> Generator[Element, None, None]:
        """
        Iterate over all elements in the collection
        :return: next element
        """
        for key in self.data:
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
        self.uid = get_uid()

    def __str__(self):
        """
        :return: string representation of the field
        """
        return f'{self.name}, {self.value}, {self.sensitive}, {self.uid}'

    def get_id(self) -> str:
        """
        Return the field unique identifier
        :return: unique identifier
        """
        return self.uid

    def to_dict(self) -> dict:
        """
        Convert field into a dictionary
        :return: dictionary with field elements (name, value, sensitive flag)
        """
        return {FIELD_NAME_KEY: self.name, FIELD_VALUE_KEY: self.value,
                FIELD_SENSITIVE_KEY: self.sensitive, FIELD_UID_KEY: str(self.uid)}

    def dump(self, indent=0):
        """
        Print the field in a human readable for. Used for debugging
        :param indent: indentation level for formatting
        """
        s = '\t' * indent + f'Field: name={self.name}, value={self.value}, sensitive={self.sensitive}, uid={self.uid}'
        print(s)


class FieldCollection(Collection):

    def to_dict(self) -> dict:
        """
        Export the item collection as a dictionary
        :return: dictionary representation
        """
        d = {}
        for key in self.data:
            f = self.data[key]
            assert isinstance(f, Field)
            d[key] = f.to_dict()
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
        self.uid = get_uid()
        self.fields = field_collection

    def __str__(self):
        """
        :return: string representation of the item
        """
        field_list = [str(f) for f in self.fields.next()]
        return f'{self.name}, {self.tags}, {self.note}, {self.time_stamp}, {self.uid}, {field_list}'

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
        for field in self.fields.next():
            yield field

    def to_dict(self):
        """
        Export the item as a dictionary
        :return: dictionary representation
        """
        return {ITEM_NAME_KEY: self.name,
                ITEM_TAG_LIST_KEY: self.tags,
                ITEM_NOTE_KEY: self.note,
                ITEM_TIMESTAMP_KEY: self.time_stamp,
                ITEM_UID_KEY: self.uid,
                ITEM_FIELDS_KEY: self.fields.to_dict()
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
        for field in self.fields.next():
            assert isinstance(field, Field)
            field.dump(indent=indent + 1)


class ItemCollection(Collection):

    def to_dict(self) -> dict:
        """
        Export the item collection as a dictionary
        :return:
        """
        d = {}
        for item_uid in self.data:
            item = self.data[item_uid]
            assert isinstance(item, Item)
            d[item_uid] = item.to_dict()
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
    print('-' * 30)
    fc1 = FieldCollection()
    fc1.add(Field('one', 1, True))
    fc1.add(Field('two', '2', False))
    print(fc1)
    print(fc1.to_dict())
    fc1.dump()

    print('-' * 30)
    fc2 = FieldCollection()
    fc2.add(Field('number', 1, True))
    fc2.add(Field('letter', 'b', False))
    fc2.add(Field('digit', '2', False))
    print(fc2)
    print(fc2.to_dict())
    fc2.dump()

    print('-' * 30)
    i1 = Item('it1', ['a', 'b'], 'note1', 1234, fc1)
    print(i1)
    print(i1.to_dict())
    i1.dump()

    print('-' * 30)
    i2 = Item('it2', ['c', 'd', 'e'], 'note2', 1000, fc2)
    print(i2)
    print(i2.to_dict())
    i2.dump()

    pass
