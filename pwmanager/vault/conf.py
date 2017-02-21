import os

class Env(object):
    ACCESS_TOKEN = 'ACCESS_TOKEN'
    APP_HANDLER_TOKEN = u'APP_HANDLER_TOKEN'
    USER_CREATOR_TOKEN = u'USER_CREATOR_TOKEN'

    @staticmethod
    def set_var(key, token):
        os.environ[key] = token

    @staticmethod
    def get_var(key):
        try:
            return os.environ[key]
        except KeyError:
            return None


class VaultResponse(object):
    SUCCESS = 200
    SUCCESS_NO_DATA = 204
    INVALID = 400
    FORBIDDEN = 403
    INVALID__PATH = 404
    HEALTH_STATUS = 429
    INTERNAL_ERROR = 500
    VAULT_MAINTENANCE = 503  # or sealed..
