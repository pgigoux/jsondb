import random
import string
from items import Item, Field

# Keys used to access the name and unique identifier in the database
# These keys are shared by items, fields and table elements
KEY_NAME = 'name'
KEY_UID = 'uid'


def random_bool() -> bool:
    """
    Return a random boolean value
    :return: random bool
    """
    return True if random.random() < 0.5 else False


def random_int(max_int=1000) -> int:
    """
    Return a random integer value
    :param max_int: maximum value
    :return: random int
    """
    return random.randrange(max_int)


def random_value() -> int | str:
    """
    Return a random int or string value
    :return: random int or string
    """
    if random.random() < 0.5:
        return random_string()
    else:
        return random_int()


def random_string(prefix='', min_length=2, max_length=20):
    """
    Return a random string with an optional prefix
    :param prefix: prefix to prepend to the string values
    :param min_length: minimum string length
    :param max_length: maximum string length
    :return: random string value
    """
    return prefix + ''.join(
        random.choice(string.ascii_letters) for i in range(random.randrange(min_length, max_length)))


def random_string_list(prefix='', min_elements=1, max_elements=5) -> list:
    """
    Return a list of random string values. The length of the list is also random.
    :param prefix: prefix to prepend to the string values
    :param min_elements: minimum number of elements in the list
    :param max_elements: maximum number of elements in the list
    :return: random list of strings
    """
    return [random_string(prefix=prefix) for _ in range(random.randrange(min_elements, max_elements))]


def random_list_element(input_list: list) -> int | str:
    """
    Return a random element from a list
    :param input_list: 
    :return: 
    """
    return input_list[random.randrange(len(input_list))]


def random_field() -> Field:
    """
    Return a field with random contents
    :return: field with random data
    """
    return Field(f'field-{random_string()}', random_value(), random_bool())


def random_field_list() -> list[Field]:
    """
    Return a variable lenght list with random fields
    :return:
    """
    return [random_field() for _ in range(random.randrange(1, 5))]


def random_item() -> Item:
    """
    Return an items with random contents
    :return:
    """
    return Item(random_string('name-'),
                random_string_list('tag-'),
                random_string('note-'),
                random_int(),
                random_field_list())


if __name__ == '__main__':
    print('bool', random_bool())
    print('int', random_int())
    print('string', random_string())
    print('value', random_value())
    print('string list', random_string_list())
    print('list element', random_list_element(list({'a': 1, 'b': 2, 'c': 3}.keys())))
