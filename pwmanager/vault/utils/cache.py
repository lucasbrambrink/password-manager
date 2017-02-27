from .crypt import SymmetricEncryption
from django.core.cache import cache
from .env import Env


class AuthCache(object):
    # todo: rotate keys
    ENCRYPTION_KEY = u'SECRET_KEY'
    NONCE_ENCRYPTION_KEY = u'NONCE_ENCRYPTION_KEY'

    @staticmethod
    def get(key):
        return cache.get(key)

    @staticmethod
    def delete(key):
        return cache.delete(key)

    @staticmethod
    def set(key, value, timeout=None):
        return cache.set(key, value, timeout)

    @classmethod
    def set_token(cls, token):
        key = SymmetricEncryption.generate_key()
        hashed_key = SymmetricEncryption.hash(key)

        encrypted_token = SymmetricEncryption.encrypt(key, token)
        cls.set(hashed_key, encrypted_token)

        return key

    @classmethod
    def get_token(cls, key):
        hashed_key = SymmetricEncryption.hash(key)
        encrypted_token = cls.get(hashed_key)

        token = None
        if encrypted_token is not None:
            token = SymmetricEncryption.decrypt(key, encrypted_token)

        return token

    @classmethod
    def set_nonce(cls, key):
        """
        set
        """
        session_key = Env.set_transient_encryption_key(cls.ENCRYPTION_KEY)
        nonce = SymmetricEncryption.generate_key()
        hnonce = SymmetricEncryption.hash(nonce.encode())
        cls.set(hnonce, SymmetricEncryption.encrypt(session_key, key))

        nonce_key = Env.set_transient_encryption_key(cls.NONCE_ENCRYPTION_KEY)
        return SymmetricEncryption.encrypt(nonce_key, nonce)

    @classmethod
    def digest_nonce(cls, nonce):
        """ consumes nonce and generates new one
            performs carry-over for token
        """
        nonce_key = Env.get_encryption_key(cls.NONCE_ENCRYPTION_KEY)
        nonce = SymmetricEncryption.decrypt(nonce_key, nonce)

        key_token = cls.get(SymmetricEncryption.hash(nonce))
        match = key_token is not None
        key = None
        if match:
            cls.delete(nonce)
            session_key = Env.get_encryption_key(cls.ENCRYPTION_KEY)
            key = SymmetricEncryption.decrypt(session_key, key_token)
            nonce = cls.set_nonce(key)
        else:
            nonce = None

        return match, nonce, key

