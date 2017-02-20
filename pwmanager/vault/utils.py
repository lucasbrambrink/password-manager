import requests
import json
import os
import uuid
from .conf import VaultResponse, Env


class VaultAPI(object):
    """
    interacts w vault over HTTP (more secure than CLI?)
    over localhost

    once authenticated, puts TOKEN in env variables
    """
    PORT = u'8200'
    HOST = u'127.0.0.1'
    PROTOCOL = u'http'  # should be https in prod obviously
    VERSION = u'v1'

    def __init__(self):
        self.token = self.get_vault_token()

    @staticmethod
    def get_vault_token():
        try:
            key = os.environ[Env.ACCESS_TOKEN]
        except KeyError:
            raise Exception(u'Unable to retrieve token')

        return key

    @classmethod
    def get_url_base(cls):
        return u'{protocol}://{host}:{port}/{version}'.format(
            protocol=cls.PROTOCOL,
            host=cls.HOST,
            port=cls.PORT,
            version=cls.VERSION,
        )

    def get_url(self, url):
        return '{}{}'.format(self.get_url_base(), url)

    def get_headers(self, is_post=False):
        """ add access token for unsealed vault """
        header = {
            u'X-Vault-Token': self.token
        }
        if is_post:
            header[u'Content-Type'] = u'application/json'

        return header

    def vget(self, url):
        return requests.get(url, headers=self.get_headers())

    def vpost(self, url, data):
        return requests.post(url, data, headers=self.get_headers(True))

    def read(self):
        url = self.get_url(u'secret/foo')
        return self.vget(url)

    def write(self, dict_obj):
        url = self.get_url(u'secret/foo')
        if u'value' not in dict_obj:
            raise Exception(u'Unable to write to vault. Incorrect formatting')

        data = json.dumps(dict_obj)
        return self.vpost(url, data)

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

    ## AppRoleAPI(object):
    """
    Role interface w/ Vault to gain temporary access tokens
    """
    def enable(self):
        url = self.get_url(u'sys/auth/approle')
        return self.vpost(url, {
            'type': "approle"
        })

    def create_approle(self, role_name):
        url = self.get_url(u'auth/approle/role/{}'.format(role_name))
        data = {
            'policies': "dev-policy,test-policy"
        }
        return self.vpost(url, data)

    def get_role_id(self, role_name):
        url = self.get_url(u'auth/approle/role/{}/role-id'.format(role_name))
        return self.vget(url)

    def create_secret_id(self, role_name):
        url = self.get_url(u'auth/approle/role/{}/secret-id'.format(role_name))
        return self.vpost(url, {})

    def login(self, role_id, secret_id):
        url = self.get_url(u'auth/approle/login')
        data = {
            'role_id': role_id,
            'secret_id': secret_id
        }
        return self.vpost(url, data)











class GuidSource(object):

    @staticmethod
    def generate():
        """generate based on hostname and current time"""
        return str(uuid.uuid1())


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
