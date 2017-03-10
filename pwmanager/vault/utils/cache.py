from .crypt import SymmetricEncryption
from django.core.cache import cache
from .mem_store import EncryptionStore


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
        session_key = EncryptionStore.get_new()
        EncryptionStore.ENCRYPTION_KEY = session_key

        nonce = SymmetricEncryption.generate_key()
        hnonce = SymmetricEncryption.hash(nonce)
        cls.set(hnonce, SymmetricEncryption.encrypt(session_key, key))

        nonce_key = EncryptionStore.get_new()
        EncryptionStore.NONCE_ENCRYPTION_KEY = nonce_key
        return SymmetricEncryption.encrypt(nonce_key, nonce)

    @classmethod
    def digest_nonce(cls, nonce):
        """ consumes nonce and generates new one
            performs carry-over for token
        """
        nonce = SymmetricEncryption.decrypt(EncryptionStore.NONCE_ENCRYPTION_KEY, nonce)

        key_token = cls.get(SymmetricEncryption.hash(nonce))
        match = key_token is not None
        key = None
        if match:
            cls.delete(nonce)
            key = SymmetricEncryption.decrypt(EncryptionStore.ENCRYPTION_KEY, key_token)
            nonce = cls.set_nonce(key)
        else:
            nonce = None

        return match, nonce, key


