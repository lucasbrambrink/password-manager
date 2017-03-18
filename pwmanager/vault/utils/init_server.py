from .otek import RollingEncryptionKeys
from .tokens import TokenApi
from .mem_store import EncryptionStore, TokenStore
from .crypt import SymmetricEncryption
from .app_role import AppRoleApi
from .policies import PolicyApi, CreateUserPolicyApi
import os

class InitializeServerEnvironment(object):

    def __init__(self):
        RollingEncryptionKeys.initialize()
        token = os.environ['ACCESS_TOKEN']
        EncryptionStore.ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        EncryptionStore.NONCE_ENCRYPTION_KEY = SymmetricEncryption.generate_key()
        TokenStore.ACCESS_TOKEN = token
        TokenApi(token)

    @classmethod
    def initalize_vault(cls, root_token):
        PolicyApi.initialize_required_policies(root_token)
        AppRoleApi.enable_approle(root_token)


    @classmethod
    def port_members(cls):
        from ..models import VaultUser
        users = VaultUser.objects.all()
        for user in users:
            c = CreateUserPolicyApi(user)
            c.create_policy_for_user()

            app = AppRoleApi()
            app.create_app_role_for_user(user.role_name)
