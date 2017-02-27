from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from .utils.crypt import SymmetricEncryption
from .utils.crypt import GuidSource
from .utils.app_role import AppRoleApi
from .utils.policies import PolicyApi, CreateUserPolicyApi
from .utils.otek import RollingEncryptionKeys


class LoginAttempt(models.Model):
    EMPTY = u'Both inputs are required'
    WRONG = u'Unable to authenticate account.'
    TOO_MANY_TRIES = u'You have tried too many times. Please wait 1 hour.'
    UNABLE_TO_MOUNT = u'Unable to connect securely to backend system.'

    email = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, null=True)
    success = models.BooleanField(default=False)
    error_msg = models.CharField(max_length=255, default=u'')


class PasswordEntity(models.Model):
    password = models.ForeignKey(to='Password')
    guid = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class Password(models.Model):
    """
    maps to login set
        maintains history via LIFO queue of password entities
    """
    vault = models.ForeignKey(to=u"Vault")
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    cookie_value = models.CharField(max_length=255, blank=True)

    @property
    def current_password(self):
        return self.passwordentity_set.objects.first()


class Vault(models.Model):
    """
    mount for individual user
    """
    key = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now_add=True, null=True)

    @staticmethod
    def init_vault(root):
        # enable AppRole
        PolicyApi.initialize_required_policies(root)
        app = AppRoleApi()
        app.enable_approle()


class VaultUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email or not username:
            raise ValueError('Users must have a username and email address')

        user = self.model(
            email=email,
            username=username,
        )

        user.set_password(password)
        user.guid = GuidSource.generate()

        vault = Vault(key=user.guid)
        vault.save()

        user.vault = vault

        # create policy for user
        c = CreateUserPolicyApi()
        c.create_policy_for_user(user.role_name)

        app_role = AppRoleApi()
        app_role.create_app_role_for_user(user.role_name)

        user.save(using=self._db)
        return user


class VaultUser(AbstractBaseUser):
    """
    django user entity that maps 1-to-1 to Vault mount
    """
    USERNAME_FIELD = u'email'
    REQUIRED_FIELDS = [u'username', u'password']
    objects = VaultUserManager()

    username = models.CharField(max_length=255, blank=False, default=u'')
    email = models.EmailField(blank=False, unique=True, default=u'')
    vault = models.OneToOneField(to=Vault,
                                 on_delete=models.CASCADE)
    guid = models.CharField(max_length=255, default=u'')
    google_authenticator_credentials = models.CharField(max_length=255, default=u'')
    nonce_e = models.CharField(max_length=255, default=u'')

    def __str__(self):
        return self.username

    @staticmethod
    def get_role_name(guid):
        return u'user{}'.format(guid)

    @property
    def role_name(self):
        return self.get_role_name(self.guid)

    def get_vault_access(self):
        app_role = AppRoleApi()
        return app_role.get_user_access_token(self.role_name)


class ApplicationToken(models.Model):
    encrypted_token = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_master_application_token(cls):
        key = RollingEncryptionKeys.get_key()
        token = cls.objects\
            .order_by('-created')\
            .first()\
            .only('hashed_token')
        dtoken = SymmetricEncryption.decrypt(key, token)
        return dtoken

    @classmethod
    def set_master_application_token(cls, token):
        key = RollingEncryptionKeys.get_key()
        token = SymmetricEncryption.encrypt(key, token)
        cls.create(encrypted_token=token)




