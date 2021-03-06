from .mem_store import TokenStore
from .vault_api import VaultConnection


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
    # POLICY NAMES
    WRITE = u'write'

    # CAPABILITIES
    CREATE = u'create'
    UPDATE = u'update'
    DELETE = u'delete'
    SUDO = u'sudo'
    PATH = u'path'

    # custom policies
    @classmethod
    def app_role_handler(cls):
        policy = PolicyConfig(u'auth/approle/role/*', cls.WRITE, None)
        return Policy(
            u'app-handler',
            [policy]
        )

    @classmethod
    def user_creator(cls):
        policy_config = PolicyConfig(u'secret/*', None,
                                     [cls.SUDO, cls.UPDATE, cls.CREATE])
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
    def delete_policy(cls, root_token, policy_name):
        api = VaultConnection(root_token)
        url = api.get_url(u'{}/{}'.format(cls.POLICY_URL, policy_name))
        return api.vdelete(url)

    @classmethod
    def initialize_required_policies(cls, root_token):
        """run once per vault"""
        api = VaultConnection(root_token)
        cls.create(api, cls.app_role_handler())
        cls.create(api, cls.user_creator())


class CreateUserPolicyApi(object):
    """
    DOES NOT WORK CURRENTLY!! TOKEN NOT STRONG ENOUGH TO CREATE user-policies
    (might need sudo?)
    """

    def __init__(self, user):
        self.user = user
        self.token = TokenStore.ACCESS_TOKEN #  TokenStore.USER_CREATOR_TOKEN
        self.api = VaultConnection(self.token)

    def create_policy_for_user(self):
        config = PolicyConfig(
            path=u'secret/{}/*'.format(self.user.role_name),
            policy_name=PolicyApi.WRITE,
        )
        policy = Policy(
            name=self.user.role_name,
            rules=[config]
        )
        return PolicyApi.create(self.api, policy)

