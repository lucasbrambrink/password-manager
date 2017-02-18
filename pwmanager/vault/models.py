from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class PasswordEntity(models.Model):
    password = models.ForeignKey(to='Password')
    created = models.DateTimeField(auto_now_add=True, null=True)
    unique_identifier = models.CharField(max_length=255)


# Create your models here.
class Password(models.Model):
    vault = models.ForeignKey(to=u"Vault")
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    # cookie_value = models.CharField(max_length=255)

    def current_password(self):
        return self.passwordentity_set.objects.first()


class Vault(models.Model):
    key = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now_add=True, null=True)


class VaultUser(AbstractBaseUser):
    vault = models.ForeignKey(to=Vault)

    def save(self, *args, **kwargs):
        if self.pk is None or self.vault is None:
            vault = Vault(key=self.username)
            vault.save()
            self.vault = vault

