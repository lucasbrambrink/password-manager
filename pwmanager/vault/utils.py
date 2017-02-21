import requests
import json
import os
import uuid
from .conf import VaultResponse, Env
from requests_toolbelt.utils import dump
import logging

log = logging.getLogger(__name__)


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
        try:
            key = os.environ[Env.ACCESS_TOKEN]
        except KeyError:
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
        else:
            log.warn(u'RESPONSE: {}'.format(response.status_code))
            log.warn(response.content)
            return response.content



class TokenApi(object):
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
        url = v.get_url(os.path.join(cls.PATH, cls.LOOKUP, token))
        return v.vget(url)

    @classmethod
    def create_token(cls, root, policies, key):
        v = VaultConnection(token=root)
        url = v.get_url(os.path.join(cls.PATH, cls.CREATE))
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



class PolicyConfig(object):

    def __init__(self, path, policy_name=None, capabilities=None):
        self.path = path
        self.policy_name = policy_name
        self.capabilities = capabilities or []


class Policy(object):

    def __init__(self, name, rules=None):
        self.name = name
        self.rules = rules or []


class PolicyApi(object):
    POLICY_URL = u'sys/policy'
    WRITE = u'write'
    CREATE = u'create'
    UPDATE = u'update'
    DELETE = u'delete'
    PATH = u'path'

    # custom policies
    @classmethod
    def app_handler(cls):
        policy = PolicyConfig(u'auth/approle/role/*', cls.WRITE, None)
        return Policy(
            u'app-handler',
            [policy]
        )

    @classmethod
    def user_creator(cls):
        policy_config = PolicyConfig(u'secret/*', None, [cls.UPDATE])
        return Policy(
            u"user-creator",
            [policy_config]
        )

    @classmethod
    def generate(cls, path, policy_name=None, capabilities=None):
        hcl = u'path "%s" { ' % path
        if policy_name is not None:
            hcl += u'policy = "{}" '.format(policy_name)
        if capabilities is not None and type(capabilities) is iter:
            hcl += u'capabilities = ["{}"]'.format(u", ".join(capabilities))
        hcl += "}"
        return hcl

    @classmethod
    def create(cls, api, policy):
        url = api.get_url(u'{}/{}'.format(cls.POLICY_URL, policy.name))
        return api.vpost(url, {
            "rules": " ".join([
                cls.generate(p.path, p.policy_name, p.capabilities)
                for p in policy.rules
            ])
        })

    @classmethod
    def initialize_required_policies(cls, root_token):
        """run once per vault"""
        api = VaultConnection(root_token)
        cls.create(api, cls.app_handler())
        cls.create(api, cls.user_creator())


class AppRoleApi(object):
    """
    AppRole interface w/ Vault to gain temporary access tokens for users

    Notes:
        policy and role have the same name
    """
    APP_ROLE_URL = u'auth/approle'
    ROLE = u'role'

    def __init__(self):
        self.token = Env.get_var(Env.APP_HANDLER_TOKEN)
        self.api = VaultConnection(token=self.token)

    def enable_approle(self):
        url = self.api.get_url(u'sys/auth/approle')
        return self.api.vpost(url, {
            'type': "approle"
        })

    def create_app_role_for_user(self, role_name):
        url = self.api.get_url(os.path.join(self.APP_ROLE_URL, self.ROLE, role_name))
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


class CreateUserPolicyApi(object):

    def __init__(self):
        self.token = Env.get_var(Env.USER_CREATOR_TOKEN)
        self.api = VaultConnection(self.token)

    def create_policy_for_user(self, role_name):
        config = PolicyConfig(
            path=u'secret/{}/*'.format(role_name),
            policy_name=PolicyApi.WRITE,
        )
        policy = Policy(
            name=role_name,
            rules=[config]
        )
        return PolicyApi.create(self.api, policy)


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
        url = os.path.join(self.base_path, key)
        resp = self.api.vget(url)
        return self.get_data(resp)

    def write(self, key, value):
        url = os.path.join(self.base_path, key)
        resp = self.api.vpost(url, {
            'value': value
        })
        return self.get_data(resp)


class GuidSource(object):

    @staticmethod
    def generate():
        """generate based on hostname and current time
                - sufficient to avoid clashes
        """
        return str(uuid.uuid1())
