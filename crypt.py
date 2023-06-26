import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# Character encoding
CHARACTER_ENCODING = 'utf-8'


class Crypt:

    def __init__(self, password: str):
        """
        Implement data encryption and decryption
        :param password:
        """
        self.key = self.generate_crypt_key(password)

    @staticmethod
    def generate_crypt_key(password: str) -> Fernet:
        """
        Generate a Fernet key from a string password
        The salt should be fixed to encrypt/decrypt consistently
        :param password: password
        :return: key
        """
        password_bytes = password.encode(CHARACTER_ENCODING)
        salt = b'TDkmQ2TyV6HRw7pW'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return Fernet(base64.urlsafe_b64encode(kdf.derive(bytes(password_bytes))))

    def encrypt(self, data: str) -> bytes:
        """
        Encrypt message using the generated key
        :param data: data to encrypt
        :return: encrypted message
        """
        return self.key.encrypt(data.encode(CHARACTER_ENCODING))

    def decrypt(self, data: bytes) -> str:
        """
        Decrypt data using the generated key
        :param data: data to decrypt
        :return: decrypted data
        """
        return self.key.decrypt(data).decode(CHARACTER_ENCODING)

    def decrypt_string(self, data: str) -> str:
        return self.key.decrypt(data.encode())


if __name__ == '__main__':
    c = Crypt('password')
    m_in = 'this is a message'
    d = c.encrypt(m_in)
    print(type(d), d)
    m_out = c.decrypt(d)
    print(type(m_out), m_out)
