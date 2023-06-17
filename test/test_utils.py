from utils import get_uid, trimmed_string, filter_control_characters


def test_uid():
    output = get_uid()
    assert isinstance(output, str)


def test_trimmed_string():
    s = 'This is a text'
    assert trimmed_string('   ' + s + '   ') == s


def test_filter_control_characters():
    s = '\t\ttext\n\r'
    assert filter_control_characters(s) == '<t><t>text<n><r>'
