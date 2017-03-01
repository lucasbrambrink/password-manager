from .otek import RollingEncryptionKeys
from .tokens import TokenApi
from .mem_store import EncryptionStore
from .crypt import SymmetricEncryption
import os

class InitializeServerEnvironment(object):

    def __init__(self):
        RollingEncryptionKeys.initialize()
        token = os.environ['ACCESS_TOKEN']
        EncryptionStore.ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        EncryptionStore.NONCE_ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        TokenApi(token)
