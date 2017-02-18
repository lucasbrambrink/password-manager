from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Password(models.Model):
    vault = models.ForeignKey(to=u"Vault")
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    # cookie_value = models.CharField(max_length=255)


class Vault(models.Model):
    user = models.ForeignKey(to=u'User')
    key = models.CharField(max_length=255)