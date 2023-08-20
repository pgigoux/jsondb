import string
import time
import re
import getpass
from datetime import datetime


class Uid:
    """
    Class used to generate unique sequential identifiers
    These identifiers are shorter than the ones generated by uuid4()
    """

    # First uid value
    FIRST_UID = 1000

    # Last uid returned
    uid_count = FIRST_UID

    # List of all uid returned. Used to check for duplicates.
    uid_list = []

    @classmethod
    def clear(cls):
        """
        Clear the class variables (testing only)
        :return:
        """
        cls.uid_count = cls.FIRST_UID
        cls.uid_list = []

    @classmethod
    def reset(cls, value=FIRST_UID):
        """
        Reset the sequential identifier count
        :param value: value used to reset the count
        """
        cls.uid_count = value

    @classmethod
    def get_uid(cls) -> int:
        """
        :return: unique identifier
        """
        cls.uid_count += 1
        if cls.uid_count not in cls.uid_list:
            cls.uid_list.append(cls.uid_count)
        else:
            raise ValueError('duplicate uid')
        return cls.uid_count

    @classmethod
    def dump(cls):
        for uid in cls.uid_list:
            print(uid)


def match_strings(pattern: str, s: str):
    """
    Check whether a regex pattern is contained into another string.
    The string matching is case insensitive.
    :param pattern: pattern to match
    :param s: string where to search
    :return: True in the string is
    """
    return True if re.search(pattern.lower(), s.lower()) else False


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
    Return a string time stamp up to the second.
    :return: time stamp
    """
    return time.strftime("%Y%m%d%H%M%S", time.gmtime())


def timestamp_to_time(time_stamp: int) -> str:
    """
    Return the local date and time corresponding to the POSIX timestamp
    Time is returned as yyyy-mm-dd hh:mm:ss
    :param time_stamp: time stamp
    :return: string representation of the time
    """
    try:
        return str(datetime.fromtimestamp(time_stamp))
    except OverflowError:
        return 'overflow'


def get_password() -> str:
    """
    Read a password from the standard input.
    :return:
    """
    return getpass.getpass('Password: ').strip()


def sensitive_mark(sensitive: bool):
    """
    Return a label that can be used to mark sensitive information in reports
    :param sensitive: sensitive information?
    :return:
    """
    return '(*)' if sensitive else '   '


def print_line(width=70):
    """
    Print an horizontal line
    :param: with: line with in characters
    """
    print(u'\u2015' * width)


def trace(label: str, *args):
    """
    Trace program execution (used in debugging)
    :param label: label
    :param args: arguments
    :return:
    """
    print(f'TRACE: {label}: ' + str([f'{x}' for x in args]))


def todo(label: str, *args):
    """
    Placeholder used for code that's not yet implemented (used in debugging)
    :param label: label
    :param args: arguments
    :return:
    """
    print(f'TODO: {label}: ' + str([f'{x}' for x in args]))


if __name__ == '__main__':
    print(Uid.get_uid())
