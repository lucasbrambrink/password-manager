from os import environ
from .crypt import SymmetricEncryption


class Env(object):
    ACCESS_TOKEN = 'ACCESS_TOKEN'
    APP_HANDLER_TOKEN = u'APP_HANDLER_TOKEN'
    USER_CREATOR_TOKEN = u'USER_CREATOR_TOKEN'

    @staticmethod
    def set_var(key, token):
        environ[key] = token

    @staticmethod
    def get_var(key):
        try:
            return environ[key]
        except KeyError:
            return None

    @classmethod
    def set_transient_encryption_key(cls, env_key):
        key = SymmetricEncryption.generate_key()
        environ[env_key] = key.decode()
        return key

    @classmethod
    def get_encryption_key(cls, env_key):
        return cls.get_var(env_key) or \
               cls.set_transient_encryption_key(env_key)
