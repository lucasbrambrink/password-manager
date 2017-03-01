from .mem_store import TokenStore
from .vault_api import VaultConnection
from os.path import join


class AppRoleException(Exception):
    """General issue for app role"""


class AppRoleApi(object):
    """
    AppRole interface w/ Vault to gain temporary access tokens for users

    Notes:
        policy and role have the same name
    """
    APP_ROLE_URL = u'auth/approle'
    ROLE = u'role'

    def __init__(self):
        self.token = TokenStore.APP_HANDLER_TOKEN
        if not self.token:
            raise Exception('App role token not provisioned')
        self.api = VaultConnection(token=self.token)

    def enable_approle(self):
        url = self.api.get_url(u'sys/auth/approle')
        return self.api.vpost(url, {
            'type': "approle"
        })

    def create_app_role_for_user(self, role_name):
        url = self.api.get_url(join(self.APP_ROLE_URL, self.ROLE, role_name))
        self.api.vpost(url, {
            "policies": role_name
        })

    def get_user_access_token(self, role_name):
        role_id = self.get_role_id(role_name)
        secret_id = self.create_secret_id(role_name)
        if None in (role_id, secret_id):
            return None

        return self.login(role_id, secret_id)

    def get_role_id(self, role_name):
        url = self.api.get_url(u'auth/approle/role/{}/role-id'.format(role_name))
        resp = self.api.vget(url)

        role_id = None
        if type(resp) is dict:
            role_id = resp\
                .get('data', {})\
                .get('role_id', None)

        return role_id

    def create_secret_id(self, role_name):
        url = self.api.get_url(u'auth/approle/role/{}/secret-id'.format(role_name))
        resp = self.api.vpost(url, {})
        secret_id = None
        if type(resp) is dict:
            secret_id = resp\
                .get('data', {})\
                .get('secret_id', {})

        return secret_id

    def login(self, role_id, secret_id):
        url = self.api.get_url(u'auth/approle/login')
        data = {
            'role_id': role_id,
            'secret_id': secret_id
        }
        resp = self.api.vpost(url, data)
        token = None
        print(resp)
        if type(resp) is dict:
            token = resp\
                .get(u'auth', {})\
                .get(u'client_token', None)
        return token
