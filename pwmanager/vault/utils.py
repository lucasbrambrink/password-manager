import requests
import json
import os
import uuid
from .conf import VaultResponse, Env
from requests_toolbelt.utils import dump
import logging

log = logging.getLogger(__name__)


class VaultApi(object):
    """
    interacts w vault over HTTP (more secure than CLI?)
    over localhost

    once authenticated, puts TOKEN in env variables
    """
    PORT = u'8200'
    HOST = u'127.0.0.1'
    PROTOCOL = u'http'  # should be https in prod obviously
    VERSION = u'v1'

    def __init__(self, token=None):
        if token is None:
            token = self.get_vault_token()
        self.token = token

    @staticmethod
    def get_vault_token():
        try:
            key = os.environ[Env.ACCESS_TOKEN]
        except KeyError:
            raise Exception(u'Unable to retrieve token')

        return key

    @classmethod
    def get_url_base(cls):
        """ gets API base url (w version) and trailing slash
        """
        return u'{protocol}://{host}:{port}/{version}/'.format(
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

    def token_authenticate(self, token):
        self.token = token
        url = self.get_url(u'auth/token')
        return self.vpost(url, data={})

    def vget(self, url):
        response = requests.get(url=url,
                                headers=self.get_headers())
        return self.handle_response(response)

    def vpost(self, url, data):
        serialized_data = json.dumps(data)
        response = requests.post(url=url,
                                 data=serialized_data,
                                 headers=self.get_headers(True))
        return self.handle_response(response)

    def vput(self, url, data):
        response = requests.put(url=url,
                                data=json.dumps(data),
                                headers=self.get_headers(True))
        data = dump.dump_all(response)
        log.debug(data.decode('utf-8'))
        return self.handle_response(response)

    def read(self):
        url = self.get_url(u'secret/foo')
        return self.vget(url)

    def write(self, dict_obj):
        url = self.get_url(u'secret/foo')
        if u'value' not in dict_obj:
            raise Exception(u'Unable to write to vault. Incorrect formatting')

        return self.vpost(url, dict_obj)

    @classmethod
    def handle_response(cls, response):
        if response.status_code == VaultResponse.SUCCESS:
            return response.json()
        else:
            log.warn(u'RESPONSE: {}'.format(response.status_code))
            log.warn(response.content)
            return response.content

    def get_password(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass


class RoleApi(VaultApi):
    """
    Role interface w/ Vault to gain temporary access tokens
    """
    def enable_approle(self):
        url = self.get_url(u'sys/auth/approle')
        return self.vpost(url, {
            'type': "approle"
        })

    def generate_policy_hcl(self, policy_name):
        """grant user write permission to their own subdirectory"""
        return u'path "secret/%s/*" { policy = "write" }' % policy_name

    def create_policy(self, policy_name):
        url = self.get_url(u'sys/policy/{}'.format(policy_name))
        data = {"rules": self.generate_policy_hcl(policy_name)}
        return self.vput(url, data)

    def create_approle(self, user_name):
        # 1-to-1 mapping of user to role, access to single path
        # generate policy for this user
        policy_name = u'user{}'.format(user_name)
        self.create_policy(policy_name)
        url = self.get_url(u'auth/approle/role/{}'.format(policy_name))
        return self.vpost(url, {
            'policies': policy_name
        })

    # Login
    def get_role_id(self, user_name):
        url = self.get_url(u'auth/approle/role/user{}/role-id'.format(user_name))
        resp = self.vget(url)

        role_id = None
        if type(resp) is dict:
            role_id = resp\
                .get('data', {})\
                .get('role_id', None)

        return role_id

    def create_secret_id(self, user_name):
        url = self.get_url(u'auth/approle/role/user{}/secret-id'.format(user_name))
        resp = self.vpost(url, {})
        secret_id = None
        if type(resp) is dict:
            secret_id = resp\
                .get('data', {})\
                .get('secret_id', {})

        return secret_id

    def login(self, role_id, secret_id):
        url = self.get_url(u'auth/approle/login')
        data = {
            'role_id': role_id,
            'secret_id': secret_id
        }
        return self.vpost(url, data)


class UserApi(object):

    def __init__(self, username, token):
        self.username = username
        self.pathname = u'user{}'.format(username)
        self.api = VaultApi(token)

    @property
    def base_path(self):
        return self.api.get_url(u'secret/{}/'.format(self.pathname))

    @staticmethod
    def get_data(resp):
        data = None
        if type(resp) is dict:
            data = resp.get(u'data', None)

        return data

    def read(self, key):
        url = os.path.join(self.base_path, key)
        resp = self.api.vget(url)
        return self.get_data(resp)

    def write(self, key, value):
        url = os.path.join(self.base_path, key)
        resp = self.api.vpost(url, {
            'value': value
        })
        return self.get_data(resp)




class GuidSource(object):

    @staticmethod
    def generate():
        """generate based on hostname and current time
                - sufficient to avoid clashes
        """
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
