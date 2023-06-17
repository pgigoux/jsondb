from typing import Generator
from common import KEY_NAME, KEY_UID
from utils import get_uid, filter_control_characters

# Field access keys
FIELD_NAME_KEY = KEY_NAME
FIELD_VALUE_KEY = 'value'
FIELD_UID_KEY = KEY_UID
FIELD_SENSITIVE_KEY = 'sensitive'

# Item access keys
ITEM_NAME_KEY = KEY_NAME
ITEM_TAG_LIST_KEY = 'tags'
ITEM_NOTE_KEY = 'note'
ITEM_TIMESTAMP_KEY = 'timestamp'
ITEM_UID_KEY = KEY_UID
ITEM_FIELDS_KEY = 'fields'


class Field:
    def __init__(self, name: str, value: str | int, sensitive=False):
        self.name = name
        self.value = value
        self.sensitive = sensitive
        self.uid = get_uid()

    def __str__(self):
        """
        :return: string representation of the field
        """
        return f'{self.name}, {self.value}, {self.sensitive}, {self.uid}'

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


class Item:
    def __init__(self, name: str, tag_list: list, note: str,
                 time_stamp: int, field_list: list[Field]):
        self.name = name
        self.tags = tag_list
        self.note = note
        self.time_stamp = time_stamp
        self.uid = get_uid()
        self.field_list = field_list

    def __str__(self):
        """
        :return: string representation of the item
        """
        field_list = [str(f) for f in self.field_list]
        return f'{self.name}, {self.tags}, {self.note}, {self.time_stamp}, {self.uid}, {field_list}'

    def to_dict(self):
        f_list = []
        for field in self.field_list:
            f_list.append(field.to_dict())
        return {ITEM_NAME_KEY: self.name,
                ITEM_TAG_LIST_KEY: self.tags,
                ITEM_NOTE_KEY: self.note,
                ITEM_TIMESTAMP_KEY: self.time_stamp,
                ITEM_UID_KEY: self.uid,
                ITEM_FIELDS_KEY: f_list
                }

    def dump(self, indent=0):
        margin = '\t' * indent
        print(margin + 'Item')
        print(margin + f'\tname={self.name}, time={self.time_stamp}, uid={self.uid}')
        note = filter_control_characters(self.note)
        # note = self.note.replace('\n', '-')
        print(margin + f'\tnote={note}')
        print(margin + f'\ttags={self.tags}')
        for field in self.field_list:
            field.dump(indent=indent + 1)


class ItemCollection:

    def __init__(self):
        self.items = {}

    def __contains__(self, uid: str):
        return uid in self.items

    def keys(self) -> list:
        """
        Return the list unique identifiers for the items in the collection
        :return:
        """
        return list(self.items.keys())

    def count(self):
        return len(self.items)

    def get(self, uid) -> Item:
        if uid in self.items:
            return self.items[uid]
        else:
            raise KeyError(f'item with uid={uid} does not exist')

    def next(self) -> Generator[Item, None, None]:
        """
        Iterate over all items in the collection
        :return: next item
        """
        for item in self.items:
            yield self.items[item]

    def add(self, item: Item):
        """
        Add item to the collection
        :param item: Item to add
        :raise: KeyError if the item already exists
        """
        if item.uid not in self.items:
            self.items[item.uid] = item
        else:
            raise KeyError(f'item with uid {item.uid} already exists')

    def remove(self, uid: str):
        """
        Remove item identified by a unique identifier
        :param uid:
        :return:
        """
        if uid in self.items:
            del self.items[uid]
        else:
            raise KeyError(f'item with uid={uid} does not exist')

    def update(self, item: Item):
        """
        Update the collection with a new instance of an item
        :param item: Item to update
        :raise: KeyError if the item does not exist already
        """
        if item.uid in self.items:
            self.items[item.uid] = Item
        else:
            raise KeyError(f'item with uid {item.uid} does not exist')

    def to_dict(self) -> dict:
        """
        Export the item collection as a dictionary
        :return:
        """
        d = {}
        for item_uid in self.items:
            item = self.items[item_uid]
            assert isinstance(item, Item)
            d[item_uid] = item.to_dict()
        return d

    def dump(self, indent=0):
        """
        Dump collection contents in a human readable form
        :param indent: indentation level
        """
        print('Items:')
        for uid in self.items:
            self.items[uid].dump(indent=indent + 1)


if __name__ == '__main__':
    pass
