# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-17 23:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0010_auto_20170315_0117'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('domain_name', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, max_length=255)),
                ('cookie_value', models.CharField(blank=True, max_length=255)),
                ('key', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalAuthentication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user_name', models.CharField(blank=True, default='', max_length=255)),
                ('domain_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault.DomainName')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='password',
            name='vault',
        ),
        migrations.AlterModelManagers(
            name='passwordentity',
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='passwordtag',
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='vault',
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='passwordentity',
            name='password',
        ),
        migrations.RemoveField(
            model_name='passwordtag',
            name='password',
        ),
        migrations.AddField(
            model_name='passwordentity',
            name='modified',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='passwordtag',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='passwordtag',
            name='modified',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='vaultuser',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='vaultuser',
            name='modified',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.DeleteModel(
            name='Password',
        ),
        migrations.AddField(
            model_name='domainname',
            name='vault',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault.Vault'),
        ),
        migrations.AddField(
            model_name='passwordentity',
            name='external_auth',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vault.ExternalAuthentication'),
        ),
        migrations.AddField(
            model_name='passwordtag',
            name='external_auth',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vault.ExternalAuthentication'),
        ),
    ]
