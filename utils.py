import uuid

# Keys used to access the name and unique identifier in the database
# These keys are shared by items, fields and table elements
KEY_NAME = 'name'
KEY_UID = 'uid'


def get_uid() -> str:
    """
    Return an unique identified in string format
    :return:
    """
    return str(uuid.uuid4())


def trimmed_string(value: str) -> str:
    """
    Trim string. Provided for convenience.
    :param value: string value to trim
    :return: trimmed string
    """
    return value.strip()


def filter_control_characters(value: str) -> str:
    """
    Filter out the most common control characters from a string
    :param value:
    :return: filtered value
    """
    return value.replace('\n', '<n>').replace('\t', '<t>').replace('\r', '<r>')


if __name__ == '__main__':
    print(get_uid())
    print('[' + trimmed_string('  text ') + ']')
    print(filter_control_characters('\ttext\t\n'))

