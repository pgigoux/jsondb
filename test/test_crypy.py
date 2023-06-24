from crypt import Crypt


def test_encryption():
    c = Crypt('password')

    m_in = 'this is a message'
    data = c.encrypt(m_in)
    assert isinstance(data, bytes)

    m_out = c.decrypt(data)
    assert isinstance(m_out, str)

    assert m_in == m_out


