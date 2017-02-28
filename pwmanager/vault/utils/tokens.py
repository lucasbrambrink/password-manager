from .vault_api import VaultConnection
from os.path import join
from .mem_store import TokenStore


class TokenApi(object):
    """
    TODO: do a periodic exchange of new tokens
    """
    PATH = u'auth/token'
    CREATE = u'create'
    LOOKUP = u'lookup'
    LOOKUP_SELF = u'lookup-self'

    #custom policies
    APP_HANDLER = u'app-handler'
    USER_CREATOR = u'user-creator'

    @classmethod
    def create_application_token(cls, root):
        """
        degraded token without root privileges
        for application to use to connect to vault
        and delegate approle
        """
        TokenStore.APP_HANDLER_TOKEN = cls.create_token(root, cls.APP_HANDLER)

    @classmethod
    def lookup_token(cls, root, token):
        v = VaultConnection(root)
        url = v.get_url(join(cls.PATH, cls.LOOKUP, token))
        return v.vget(url)

    @classmethod
    def create_token(cls, root, policies):
        v = VaultConnection(token=root)
        url = v.get_url(join(cls.PATH, cls.CREATE))
        data = {
            "policies": [policies]
        }
        resp = v.vpost(url, data)
        token = None
        if type(resp) is dict:
            token = resp\
                .get(u'auth', {})\
                .get(u'client_token', None)

        return token

    @classmethod
    def create_user_creator_token(cls, root):
        """
        degraded token without root privileges
        for application to use to connect to vault
        and delegate approle
        """
        TokenStore.USER_CREATOR_TOKEN = cls.create_token(root, cls.USER_CREATOR)

    def __init__(self, root):
        self.create_application_token(root)
        self.create_user_creator_token(root)

