import requests
import json
import os
from .conf import VaultResponse


class VaultAPI(object):
    """
    interacts w vault over HTTP (more secure than CLI?)
    over localhost

    once authenticated, puts TOKEN in env variables
    """
    PORT = u'8200'
    HOST = u'127.0.0.1'
    PROTOCOL = u'https'
    VERSION = u'v1'

    def __init__(self, token_key):
        self.token_key = token_key
        self.token = self.get_vault_token()

    def get_vault_token(self):
        key = os.environ(self.token_key)
        if key is None:
            raise Exception(u'Unable to retrieve token')

        return key

    def get_url(self, mount, key):
        return u'{protocol}://{host}:{port}/{version}/{mount}/{key}'.format(
            protocol=self.PROTOCOL,
            host=self.HOST,
            port=self.PORT,
            version=self.VERSION,
            mount=mount,
            key=key
        )

    def get_headers(self, is_post=False):
        """ add access token for unsealed vault """
        header = {
            u'X-Vault-Token': self.token
        }
        if is_post:
            header[u'Content-Type'] = u'application/json'

        return header

    def read(self):
        url = self.get_url(u'secret', u'foo')
        return requests.get(url, headers=self.get_headers())

    def write(self, dict_obj):
        url = self.get_url(u'secret', u'foo')
        if u'value' not in dict_obj:
            raise Exception(u'Unable to write to vault. Incorrect formatting')

        data = json.dumps(dict_obj)
        return requests.post(
            url,
            data=data,
            headers=self.get_headers(True))

    @classmethod
    def handle_response(cls, response):
        if response.status_code == VaultResponse.SUCCESS:
            return response.content
        else:
            raise Exception(response.status_code)

    def get_password(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass


class GuidSource(object):


    @staticmethod
    def generate():
        return u'asdfasdfads'


# from Crypto.Hash import SHA512
# from Crypto.Cipher import AES
# from Crypto.Util import randpool
#
#
# class HashingHandler(object):
#     SALT_SIZE = 126
#     ITERATIONS = 20
#     AES_BYTE_LENGTH = 16
#
#     @classmethod
#     def generate_key(cls, encryption_key, salt):
#         key = encryption_key + salt
#         for i in range(cls.ITERATIONS):
#             key = SHA512.new(key).digest()
#
#         return key
#
#     @classmethod
#     def pad_key(cls, key):
#         extra_bytes = len(key) % cls.AES_BYTE_LENGTH
#         padding_size = cls.AES_BYTE_LENGTH - extra_bytes
#         padding = chr(padding_size) * padding_size
#         return key + padding
#
#     @classmethod
#     def strip_padding(cls, padded_key):
#         padding_size = ord(padded_key[-1])
#         return padded_key[:-padding_size]
#
#     @classmethod
#     def get_salt(cls):
#         pool = randpool.RandomPool()
#         return pool.get_bytes(cls.SALT_SIZE)
#
#     @classmethod
#     def encrypt(cls, plain_text, encryption_key):
#         salt = cls.get_salt()
#         key = cls.generate_key(encryption_key, salt)
#         key = cls.pad_key(key)
#         cipher = AES.new(key, AES.MODE_ECB)
#         cipher_text = cipher.encrypt(plain_text)
#         return salt + cipher_text
#
#     @classmethod
#     def decrypt(cls, cipher_text, encryption_key):
#         salt, ctext = cipher_text[:cls.SALT_SIZE], cipher_text[cls.SALT_SIZE:]
#         key = cls.generate_key(encryption_key, salt)
#         cipher = AES.new(key, AES.MODE_ECB)
#         return cipher.decrypt(ctext)
#
#
