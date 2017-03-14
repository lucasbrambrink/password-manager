from cryptography.fernet import Fernet, base64, InvalidSignature, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import hashlib
import os
import uuid
from django.contrib.auth.hashers import make_password, PBKDF2PasswordHasher, BasePasswordHasher


class SymmetricEncryption(object):

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    @staticmethod
    def safe_encode(value):
        if type(value) is str:
            value = value.encode('utf-8')
        return base64.urlsafe_b64encode(value)

    @staticmethod
    def generate_salt():
        return BasePasswordHasher().salt()
        # p = base64.urlsafe_b64encode(password.encode('utf-8')).decode()
        # return os.urandom(length)

    # @classmethod
    # def generate_key_from_password(cls, password_hash):
    #     # archive encryption key
    #     salt = cls.generate_salt()
    #     decoded_salt = base64.urlsafe_b64encode(salt).decode('utf-8')
    #     return cls.build_encryption_key(password, decoded_salt), decoded_salt

    @classmethod
    def build_encryption_key(cls, password_hash):
        # if type(password_hash) is str:
        #     salt = password_hash.encode('utf-8')
        # salted_string = base64.urlsafe_b64encode(password.encode('utf-8')) + salt

        reduced = password_hash[:32].encode('utf-8')
        return base64.urlsafe_b64encode(reduced)

    @staticmethod
    def encrypt(key, secret):
        if type(key) is bytes:
            pass
        if type(secret) is str:
            secret = secret.encode('utf-8')
        if type(secret) is not bytes:
            raise TypeError('%s: Encryption requires string or bytes' % type(secret))

        return Fernet(key).encrypt(secret)

    @staticmethod
    def decrypt(key, token):
        return Fernet(key).decrypt(token)

    @staticmethod
    def hash(key):
        return hashlib.sha512(key).hexdigest()


class RSA(object):

    @staticmethod
    def generate_private_key():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )


class GuidSource(object):

    @staticmethod
    def generate():
        """generate based on hostname and current time
                - sufficient to avoid clashes
        """
        return str(uuid.uuid1())