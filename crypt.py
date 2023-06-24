import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


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
        :param password: password
        :return: key
        """
        password_bytes = password.encode('utf-8')
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return Fernet(base64.urlsafe_b64encode(kdf.derive(bytes(password_bytes))))

    def encrypt(self, message: str) -> bytes:
        """
        Encode message using the generated key
        :param message: message to encode
        :return: encoded message
        """
        return self.key.encrypt(message.encode('utf-8'))

    def decrypt(self, data: bytes) -> str:
        """
        Decode data using the generated key
        :param data:
        :return:
        """
        return self.key.decrypt(data).decode('utf-8')


if __name__ == '__main__':
    c = Crypt('password')
    m_in = 'this is a message'
    d = c.encrypt(m_in)
    print(type(d), d)
    m_out = c.decrypt(d)
    print(type(m_out), m_out)
