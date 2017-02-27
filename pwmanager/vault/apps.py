from __future__ import unicode_literals
from .utils.init_server import InitializeServerEnvironment
from django.apps import AppConfig


class VaultConfig(AppConfig):
    name = 'vault'

    def ready(self):
        InitializeServerEnvironment()

