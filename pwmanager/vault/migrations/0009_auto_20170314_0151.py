# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0008_auto_20170314_0106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vaultuser',
            name='guid_e',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]