from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .utils import GuidSource


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


class VaultUser(AbstractBaseUser):
    """
    django user entity that maps 1-to-1 to Vault mount
    """
    vault = models.OneToOneField(to=Vault)
    guid = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.vault is None:
            vault = Vault(key=self.username)
            vault.save()
            self.vault = vault

        if self.guid is None:
            self.guid = GuidSource.generate()

        super(VaultUser, self).save(*args, **kwargs)

