from .crypt import SymmetricEncryption
from .env import Env
import logging


class RollingEncryptionKeys(object):
    """
    - take seed (never stored)
    -> go forever, map to e-keys to ???
    -> daemon to ping?
    -> generate random seed
    """
    TRANSIENT_E_KEY = u'NON_LOCAL_TIME_HASH'

    @staticmethod
    def roll_encryption(original_key, new_key, token_e):
        token = SymmetricEncryption.decrypt(original_key, token_e)
        return SymmetricEncryption.encrypt(new_key, token)

    @classmethod
    def roll_all(cls, original_key, new_key, obj_array):
        """
        :obj_array: [] of .get & .set objects
        TODO: db write should be optimized
        """
        for obj in obj_array:
            token_e = obj.get()
            obj.set(
                cls.roll_encryption(original_key, new_key, token_e)
            )

    def initialize(self, seed):
        Env.set_var(self.TRANSIENT_E_KEY, seed)

    @classmethod
    def get_key(cls):
        key = Env.get_var(cls.TRANSIENT_E_KEY)
        if not key:
            raise Exception('Process environment not provisioned')

        return key

    def update(self, updates):
        key = self.get_key()
        new_key = SymmetricEncryption.generate_key()
        Env.set_var(self.TRANSIENT_E_KEY, new_key)
        self.roll_all(key, new_key, updates)

