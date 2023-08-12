import random
import string
from items import Item, Field, FieldCollection

RANDOM_WORDS = ['cow', 'horse', 'sheep', 'duck', 'chicken', 'donkey',
                'apple', 'orange', 'banana', 'tomato', 'avocado', 'parsley',
                'proton', 'neutron', 'electron', 'muon', 'tau', 'neutrino']

RANDOM_EMAIL_SERVERS = ['gmail.com', 'hotmail.com', 'yahoo.com', 'yahoo.es', 'outlook.com']

RANDOM_WEB_SERVERS = ['www.nowhere.com', 'www.somewhere.com', 'www.somebody.com', 'www.nobody.com',
                      'www.something.com', 'www.nothing.com', 'www.top.com', 'www.bottom.com']


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
        random.choice(string.ascii_letters) for _ in range(random.randrange(min_length, max_length)))


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


def random_web_server() -> str:
    """
    Return random a web server name from a list of choices
    :return: random web server
    """
    return f'https://{RANDOM_WEB_SERVERS[random_int(max_int=len(RANDOM_WEB_SERVERS) - 1)]}'


def random_email() -> str:
    """
    Return a random email of the form 'jdoe<number>@<server>'
    :return: random email address
    """
    return f'jdoe{str(random_int(max_int=5000))}@' + \
           f'{RANDOM_EMAIL_SERVERS[random_int(max_int=len(RANDOM_EMAIL_SERVERS) - 1)]}'


def random_password():
    """
    Return a random password of the for <word>-<word>-<word>
    :return: random passord
    """
    n_max = len(RANDOM_WORDS) - 1
    return f'{RANDOM_WORDS[random_int(max_int=n_max)]}-' + \
           f'{RANDOM_WORDS[random_int(max_int=n_max)]}-' + \
           f'{RANDOM_WORDS[random_int(max_int=n_max)]}'


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


def random_field_collection() -> FieldCollection:
    """
    Return a random field collection
    :return:
    """
    fc = FieldCollection()
    for _ in range(random.randrange(1, 5)):
        fc.add(random_field())
    return fc


def random_item() -> Item:
    """
    Return an items with random contents
    :return:
    """
    return Item(random_string('name-'),
                random_string_list('tag-'),
                random_string('note-'),
                random_int(),
                random_field_collection())


if __name__ == '__main__':
    print('email', random_email())
    print('password', random_password())
    print('web', random_web_server())
    print('bool', random_bool())
    print('int', random_int())
    print('string', random_string())
    print('value', random_value())
    print('string list', random_string_list())
    print('list element', random_list_element(list({'a': 1, 'b': 2, 'c': 3}.keys())))
    random_item().dump()
