import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class EncryptDecrypt:

    def __init__(self, path):
        self.path = path

    verbosity = None

    @staticmethod
    def create_key(password):
        salt = b'\xda\x01\xac\x87\xe9<\xef\x13\xdd\xa2\x08\xce\xbd\xbb\x93\xd7'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key


class Decryption(EncryptDecrypt):
    def execute(self, password):
        with open(self.path, 'r') as file:
            data_to_decrypt = file.read()
        fernet = Fernet(self.create_key(password))
        decrypt_content = fernet.decrypt(data_to_decrypt.encode('utf-8'))
        with open(self.path.rename(self.path.with_suffix('.txt')), 'w') as file:
            file.write(decrypt_content.decode('utf-8'))


class Encryption(EncryptDecrypt):
    def execute(self, password):
        with open(self.path, 'r') as file:
            data_to_encrypt = file.read()
        fernet = Fernet(self.create_key(password))
        encrypted_content = fernet.encrypt(data_to_encrypt.encode('utf-8'))
        with open(self.path.rename(self.path.with_suffix('.secret')), 'w') as file:
            file.write(encrypted_content.decode('utf-8'))


class Append(EncryptDecrypt):
    def __init__(self, path, text):
        self.text = text.encode('utf-8')
        super().__init__(path)

    def execute(self, password):
        # red file
        with open(self.path, 'r') as file:
            data = file.read()
        # decrypt file
        fernet = Fernet(self.create_key(password))
        decrypted_contend = fernet.decrypt(data.encode('utf-8'))
        # append text
        decrypted_contend += b'\n'
        decrypted_contend += self.text
        # encryption file
        with open(self.path, 'w') as file:
            file.write(decrypted_contend.decode('utf-8'))
