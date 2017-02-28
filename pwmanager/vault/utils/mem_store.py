from .crypt import SymmetricEncryption


class TokenStore(object):
    ACCESS_TOKEN = None
    APP_HANDLER_TOKEN = None
    USER_CREATOR_TOKEN = None


class EncryptionStore(object):
    ENCRYPTION_KEY = None
    NONCE_ENCRYPTION_KEY = None
    TRANSIENT_E_KEY = None

    @classmethod
    def get_new(cls):
        key = SymmetricEncryption.generate_key()
        return key.decode()

    @classmethod
    def get_encryption_key(cls, env_key):
        return cls.__dict__.get(env_key)

