import requests


class VaultAPI(object):

    def create(self):

        pass

    def get_password(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass





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
