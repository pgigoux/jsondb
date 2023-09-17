from utils import match_strings, trimmed_string, filter_control_characters


# def test_uid():
#
#     Uid.clear()
#     assert Uid.get_uid() == Uid.FIRST_UID + 1
#
#     uid_1 = Uid.get_uid()
#     assert isinstance(uid_1, int)
#
#     uid_2 = Uid.get_uid()
#     assert isinstance(uid_2, int)
#
#     assert uid_2 == uid_1 + 1
#
#     # force a duplicate
#     with pytest.raises(ValueError):
#         Uid.reset()
#         _ = Uid.get_uid()


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


if __name__ == '__main__':
    pass
