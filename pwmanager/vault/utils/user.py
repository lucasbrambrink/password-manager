from .vault_api import VaultConnection
from os.path import join
from .crypt import SymmetricEncryption

class UserApi(object):

    def __init__(self, role_name, token, encryption_key):
        self.encryption_key = encryption_key
        self.role_name = role_name
        self.api = VaultConnection(token)

    @property
    def base_path(self):
        return self.api.get_url(u'secret/{}/'.format(self.role_name))

    def get_data(self, resp):
        data = {}
        if type(resp) is dict:
            data = resp.get(u'data', {})

        value = data.get('value', None)
        if value:
            value = SymmetricEncryption.decrypt(self.encryption_key, value.encode('utf-8'))

        return value.decode()

    def read(self, key):
        url = join(self.base_path, key)
        resp = self.api.vget(url)
        return self.get_data(resp)

    def write(self, key, value):
        value_e = SymmetricEncryption.encrypt(self.encryption_key, value)
        url = join(self.base_path, key)
        resp = self.api.vpost(url, {
            'value': value_e.decode()
        })
        return type(resp) is dict
