from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from .utils.crypt import SymmetricEncryption
from .utils.crypt import GuidSource
from .utils.app_role import AppRoleApi
from .utils.policies import PolicyApi, CreateUserPolicyApi
from .utils.otek import RollingEncryptionKeys
from .utils.vault_api import VaultException
from .utils.user import UserApi
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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
    is_active = models.BooleanField(default=True)


class PasswordManager(models.Manager):

    def history(self):
        return

    def create_password(self, user, token, domain_name, password, user_key, password_guid=None):
        api = user.access_api(token, user_key)
        entity = PasswordEntity(
            guid=GuidSource.generate(),
        )
        success = api.write(entity.guid, password)
        if not success:
            raise VaultException("Unable to write to vault")

        password_obj = None
        if password_guid:
            try:
                password_obj = Password.objects.get(key=password_guid)
            except Password.DoesNotExist:
                pass

        password_obj = password_obj or self.model(
            vault=user.vault,
            key=GuidSource.generate()
        )
        password_obj.domain_name = domain_name
        password_obj.save(using=self._db)
        entity.password = password_obj
        entity.save(using=self._db)


class Password(models.Model):
    """
    maps to login set
        maintains history via LIFO queue of password entities
    """
    objects = PasswordManager()

    vault = models.ForeignKey(to=u"Vault")
    domain_name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    cookie_value = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def current_password(self):
        return self.passwordentity_set.objects.first()

    def soft_delete(self):
        self.is_active = False
        self.save()


class Vault(models.Model):
    """
    mount for individual user
    """
    key = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

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
        c = CreateUserPolicyApi(user)
        c.create_policy_for_user()

        app_role = AppRoleApi()
        app_role.create_app_role_for_user(user.role_name)

        user.save(using=self._db)
        return user

    def set_password(self, user, password):
        encryption_key, salt = SymmetricEncryption.generate_key_from_password(password)
        user.set_password(password)
        user.salt = salt


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
    salt = models.CharField(max_length=255, default=u'')
    guid = models.CharField(max_length=255, default=u'')
    google_authenticator_credentials = models.CharField(max_length=255, default=u'')
    nonce_e = models.CharField(max_length=255, default=u'')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    @staticmethod
    def get_role_name(guid):
        return u'user{}'.format(guid)

    @property
    def role_name(self):
        return self.get_role_name(self.guid)

    def access_api(self, token, encryption_key):
        return UserApi(self.role_name, token, encryption_key)

    def get_vault_access(self):
        app_role = AppRoleApi()
        return app_role.get_user_access_token(self.role_name)

    def set_password(self, raw_password):
        super(VaultUser, self).set_password(raw_password)
        # archive encryption key
        encryption_key, salt = SymmetricEncryption.generate_key_from_password(raw_password)
        self.salt = salt
        return salt


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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)