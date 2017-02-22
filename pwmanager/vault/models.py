from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password
from .utils import GuidSource, CreateUserPolicyApi, AppRoleApi, UserApi, AuthCache
from .conf import Env
import hashlib
import random



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
    nonce = models.CharField(max_length=255, default=u'')

    def __str__(self):
        return self.username

    def carry_over_access_token(self, nonce):

        token = Env.get_var(self.nonce)
        if not token:
            return False

        Env.set_var(self.nonce, None)
        Env.set_var(nonce, token)
        self.nonce = nonce
        return True

    def set_nonce(self):
        self.nonce = GuidSource.generate()
        self.save()
        return self.hash(self.nonce)

    def digest_nonce(self, nonce):
        """consumes nonce and generates new one"""
        match = False
        if self.hash(self.nonce) == nonce:
            match = True

        nonce = self.set_nonce()
        return match, nonce

    def get_token(self):
        return Env.get_var(self.nonce)


    @staticmethod
    def get_role_name(guid):
        return u'user{}'.format(guid)

    @property
    def role_name(self):
        return self.get_role_name(self.guid)

    def get_vault_access(self):
        app_role = AppRoleApi()
        return app_role.get_user_access_token(self.role_name)

    def get_authenticated_access(self):
        token = self.get_token()
        if not token:
            raise Exception('Unable to access vault')

        return UserApi(self.role_name, token)

    # def authenticate(self, username, password):
    #     if not username or not password:
    #         return None
    #
    #     try:
    #         user = self.objects.get(username=username)
    #     except VaultUser.DoesNotExist:
    #         return None
    #
    #     valid_pass = check_password(password, user.password)
    #     if not valid_pass:
    #         return None
    #
    #     return self




