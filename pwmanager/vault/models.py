from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password
from .utils import GuidSource, CreateUserPolicyApi, AppRoleApi, UserApi
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
    unique_identifier = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.guid is None:
            guid = GuidSource.generate()
            self.guid = u'{}{}'.format(self.password.pk, guid)
        super(VaultUser, self).save(*args, **kwargs)


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
    first_hash = models.CharField(max_length=255, default='')
    second_hash = models.CharField(max_length=255, default='')
    first_iteration = models.IntegerField(default=10)
    second_iteration = models.IntegerField(default=10)

    def __str__(self):
        return self.username

    def authenticate_to_vault(self):
        app_role_api = AppRoleApi()
        token = app_role_api.get_user_access_token(self.role_name)
        if token is not None:
            self.set_first_nonce()
            Env.set_var(self.nonce, token)

        return token is not None

    def set_first_nonce(self):
        self.nonce = GuidSource.generate()
        self.first_iteration = random.randint(10, 25)
        hashed_nonce = self.nonce
        for x in range(self.first_iteration):
            hashed_nonce = self.hash(hashed_nonce)

        self.first_hash = hashed_nonce
        self.save()

    def set_second_nonce(self):
        self.second_iteration = random.randint(10, 25)
        second_hash = self.first_hash
        for x in range(self.second_iteration):
            second_hash = self.hash(second_hash)

        self.second_hash = second_hash
        self.save()

    def match_first_nonce(self, hashed_nonce):
        original = self.nonce
        for x in range(self.first_iteration):
            original = self.hash(original)

        return original == hashed_nonce

    def match_both_nonces(self, first_hash, second_hash):
        test = self.nonce
        for x in range(self.first_iteration):
            test = self.hash(test)

        if not test == self.first_hash:
            return False

        for x in range(self.second_iteration):
            test = self.hash(test)

        return test == self.second_hash

    def get_token(self):
        return Env.get_var(self.nonce)

    @staticmethod
    def hash(key):
        return hashlib.sha512(key).hexdigest()

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




