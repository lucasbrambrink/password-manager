from .vault_api import VaultConnection
from os.path import join


class UserApi(object):

    def __init__(self, role_name, token):
        self.role_name = role_name
        self.api = VaultConnection(token)

    @property
    def base_path(self):
        return self.api.get_url(u'secret/{}/'.format(self.role_name))

    @staticmethod
    def get_data(resp):
        data = None
        if type(resp) is dict:
            data = resp.get(u'data', None)

        return data

    def read(self, key):
        url = join(self.base_path, key)
        resp = self.api.vget(url)
        return self.get_data(resp)

    def write(self, key, value):
        url = join(self.base_path, key)
        resp = self.api.vpost(url, {
            'value': value
        })
        return type(resp) is dict
