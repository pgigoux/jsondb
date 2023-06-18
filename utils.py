import string
import uuid
import time
import re


def get_uid() -> str:
    """
    Return an unique identified in string format
    :return:
    """
    return str(uuid.uuid4())


def match_strings(s1: str, s2: str):
    return True if re.search(s1.lower(), s2.lower()) else False


def trimmed_string(value: str) -> str:
    """
    Trim string. Provided for convenience.
    :param value: string value to trim
    :return: trimmed string
    """
    return value.strip()


def filter_control_characters(value: str) -> str:
    """
    Replace control characters from a string with a '<n>' equivalent.
    Used for debugging.
    :param value:
    :return: filtered value
    """
    o_str = ''
    for c in value:
        if c in string.printable and c not in string.whitespace or c == ' ':
            o_str += c
        else:
            o_str += '<' + str(ord(c)) + '>'
    return o_str


def timestamp() -> str:
    """
    Return a string time stamp that can be used in file names
    :return: time stamp
    """
    return time.strftime("%Y%m%d%H%M%S", time.gmtime())


if __name__ == '__main__':
    # print(filter_control_characters('\rabc\t\n'))
    # print(time_stamp())
    pass
