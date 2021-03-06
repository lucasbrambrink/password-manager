# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 23:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='password',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='passwordentity',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='vault',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='vaultuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
