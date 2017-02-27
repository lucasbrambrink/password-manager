from .vault_api import VaultConnection
from os.path import join
from .env import Env


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
        return cls.create_token(root, cls.APP_HANDLER, Env.APP_HANDLER_TOKEN)

    @classmethod
    def lookup_token(cls, root, token):
        v = VaultConnection(root)
        url = v.get_url(join(cls.PATH, cls.LOOKUP, token))
        return v.vget(url)

    @classmethod
    def create_token(cls, root, policies, key):
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

        if token is not None:
            Env.set_var(key, token)
        return token

    @classmethod
    def create_user_creator_token(cls, root):
        """
        degraded token without root privileges
        for application to use to connect to vault
        and delegate approle
        """
        return cls.create_token(root, cls.USER_CREATOR, Env.USER_CREATOR_TOKEN)

    def __init__(self, root):
        self.create_application_token(root)
        self.create_user_creator_token(root)

