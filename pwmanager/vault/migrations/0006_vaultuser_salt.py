# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-10 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0005_vaultuser_decryption_key_e'),
    ]

    operations = [
        migrations.AddField(
            model_name='vaultuser',
            name='salt',
            field=models.CharField(default='', max_length=255),
        ),
    ]
