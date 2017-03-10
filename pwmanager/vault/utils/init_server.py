from .otek import RollingEncryptionKeys
from .tokens import TokenApi
from .mem_store import EncryptionStore
from .crypt import SymmetricEncryption
from .app_role import AppRoleApi
from .policies import PolicyApi
import os

class InitializeServerEnvironment(object):

    def __init__(self):
        RollingEncryptionKeys.initialize()
        token = os.environ['ACCESS_TOKEN']
        EncryptionStore.ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        EncryptionStore.NONCE_ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        TokenApi(token)

    def initalize_vault(self, root_token):
        PolicyApi.initialize_required_policies(root_token)
        AppRoleApi.enable_approle(root_token)