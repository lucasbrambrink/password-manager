from cryptography.fernet import Fernet
import hashlib
import random


class SymmetricEncryption(object):

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    @staticmethod
    def encrypt(key, secret):
        if type(secret) is str:
            secret = secret.encode('utf-8')
        if type(secret) is not bytes:
            raise Exception('Encryption requires string or bytes')
        return Fernet(key).encrypt(secret)

    @staticmethod
    def decrypt(key, token):
        return Fernet(key).decrypt(token)

    @staticmethod
    def hash(key):
        return hashlib.sha512(key).hexdigest()

    @staticmethod
    def generate_password(length=16):
        lowercase = u'abcdefghijklmnopqrstuvwxyz'
        upppercase = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '1234567890'
        symbols = '!@#$%^&*+=?'
        choices = [
            lowercase,
            upppercase,
            numbers,
            symbols
        ]

        password = []
        for x in range(length):
            category = random.choice(choices)
            password.append(random.choice(category))

        return u''.join(password)
