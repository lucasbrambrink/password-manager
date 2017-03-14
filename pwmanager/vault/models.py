from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password, PBKDF2PasswordHasher, BasePasswordHasher
from .utils.crypt import SymmetricEncryption
from .utils.crypt import GuidSource, InvalidToken, InvalidSignature
from .utils.app_role import AppRoleApi
from .utils.policies import PolicyApi, CreateUserPolicyApi
from .utils.otek import RollingEncryptionKeys
from .utils.vault_api import VaultException
from .utils.user import UserApi
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import logging
import base64
log = logging.getLogger(__name__)


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
    external_unique_identifier = models.CharField(max_length=255, default=u'')
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
        user.password = 'Nothing here...'
        # create policy for user
        c = CreateUserPolicyApi(user)
        c.create_policy_for_user()

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
    salt = models.CharField(max_length=255, default=u'')
    guid = models.CharField(max_length=255, default=u'')
    guid_e = models.BinaryField(null=True, blank=True)
    google_authenticator_credentials = models.CharField(max_length=255, default=u'')
    nonce_e = models.CharField(max_length=255, default=u'')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    @staticmethod
    def get_role_name(guid):
        return u'user{}'.format(guid)

    def check_password(self, raw_password):
        password = self.make_password(raw_password)
        encryption_key = SymmetricEncryption.build_encryption_key(password)
        try:
            # if type(self.guid_e) is str:
            self.guid_e = bytes(self.guid_e)#     self.guid_e = self.guid_e.encode('utf-8')
            guid = SymmetricEncryption.decrypt(
                encryption_key,
                self.guid_e)
            return guid.decode() == self.guid
        except InvalidSignature:
            log.warning("Invalid signature")
            return False
        except InvalidToken:
            log.warning("Invalid token")
            return False

    def make_password(self, raw_password):
        hasher = PBKDF2PasswordHasher()
        hashed_password = hasher.encode(raw_password, self.salt)
        return hashed_password.split('$').pop()

    @property
    def role_name(self):
        return self.get_role_name(self.guid)

    def access_api(self, token, encryption_key):
        return UserApi(self.role_name, token, encryption_key)

    def get_vault_access(self):
        app_role = AppRoleApi()
        return app_role.get_user_access_token(self.role_name)

    def set_password(self, raw_password):
        """" encrypt guid w gen. encryption key """
        self.salt = SymmetricEncryption.generate_salt()
        password = self.make_password(raw_password)
        encryption_key = SymmetricEncryption.build_encryption_key(password)
        self.guid_e = SymmetricEncryption.encrypt(encryption_key, self.guid)
        self.save(update_fields=['guid_e'])


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