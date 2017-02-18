from django.db import models


class Password(models.Model):
    vault = models.ForeignKey(to=u"Vault")
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    cookie_value = models.CharField(max_length=255)


class VaultUser(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)


class Vault(models.Model):
    user = models.ForeignKey(to=u'VaultUser')
    key = models.CharField(max_length=255)
