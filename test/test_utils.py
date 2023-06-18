from utils import get_uid, match_strings, trimmed_string, filter_control_characters


def test_uid():
    output = get_uid()
    assert isinstance(output, str)


def test_trimmed_string():
    s = 'This is a text'
    assert trimmed_string('   ' + s + '   ') == s


def test_match_strings():
    assert match_strings('one', 'two') is False
    assert match_strings('is', 'This is a string') is True
    assert match_strings('The.story', 'The story of') is True


def test_filter_control_characters():
    s = '\t\ttext\n\r'
    assert filter_control_characters(s) == '<9><9>text<10><13>'
