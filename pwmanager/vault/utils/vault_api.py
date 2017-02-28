from .mem_store import TokenStore
import requests
import logging
import json
"""
TODO:
    - use event store to write all traffic permanently
    - create orphan token of root
    -


"""


log = logging.getLogger(__name__)


class VaultResponse(object):
    SUCCESS = 200
    SUCCESS_NO_DATA = 204
    INVALID = 400
    FORBIDDEN = 403
    INVALID__PATH = 404
    HEALTH_STATUS = 429
    INTERNAL_ERROR = 500
    VAULT_MAINTENANCE = 503  # or sealed..


class VaultException(Exception):
    pass


class VaultConnection(object):
    """
    interacts w vault over HTTP (more secure than CLI?)
    over localhost

    once authenticated, puts TOKEN in env variables
    """
    PORT = u'8200'
    HOST = u'127.0.0.1'
    PROTOCOL = u'http'  # should be https in prod obviously
    VERSION = u'v1'

    def __init__(self, token=None):
        if token is None:
            token = self.get_vault_token()
        self.token = token

    @staticmethod
    def get_vault_token():
        key = TokenStore.ACCESS_TOKEN
        if not key:
            raise Exception(u'Unable to retrieve token')

        return key

    @classmethod
    def get_url_base(cls):
        """ gets API base url (w version) and trailing slash
        """
        return u'{protocol}://{host}:{port}/{version}/'.format(
            protocol=cls.PROTOCOL,
            host=cls.HOST,
            port=cls.PORT,
            version=cls.VERSION,
        )

    def get_url(self, url):
        return '{}{}'.format(self.get_url_base(), url)

    def get_headers(self, is_post=False):
        """ add access token for unsealed vault """
        header = {
            u'X-Vault-Token': self.token
        }
        if is_post:
            header[u'Content-Type'] = u'application/json'

        return header

    def token_authenticate(self, token):
        self.token = token
        url = self.get_url(u'auth/token')
        return self.vpost(url, data={})

    def vget(self, url):
        response = requests.get(url=url,
                                headers=self.get_headers())
        return self.handle_response(response)

    def vpost(self, url, data):
        serialized_data = json.dumps(data)
        response = requests.post(url=url,
                                 data=serialized_data,
                                 headers=self.get_headers(True))
        return self.handle_response(response)

    def vput(self, url, data):
        response = requests.put(url=url,
                                data=json.dumps(data),
                                headers=self.get_headers(True))
        data = dump.dump_all(response)
        log.debug(data.decode('utf-8'))
        return self.handle_response(response)

    @classmethod
    def handle_response(cls, response):
        if response.status_code == VaultResponse.SUCCESS:
            log.info(response.json())
            return response.json()
        elif response.status_code == VaultResponse.SUCCESS_NO_DATA:
            log.info(response)
            return {}
        else:
            log.warn(u'RESPONSE: {}'.format(response.status_code))
            log.warn(response.content)
            return response.content

