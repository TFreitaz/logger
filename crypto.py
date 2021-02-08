import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

HASH_SECRET_KEY = os.getenv("HASH_SECRET_KEY")  # open("secret.key", "rb").read()


class Crypto:
    def __init__(self):
        self.key = HASH_SECRET_KEY

    def encrypt(self, message):
        encoded_message = message.encode()
        f = Fernet(self.key)
        encrypted_message = f.encrypt(encoded_message)
        return encrypted_message

    def decrypt(self, encrypted_message):
        f = Fernet(self.key)
        decrypted_message = f.decrypt(encrypted_message)

        return decrypted_message.decode()
