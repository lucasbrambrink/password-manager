from django.conf.urls import url
from .views.authentication import AuthenticationView, ChromeExtensionLoginView
from .views.registration import RegistrationView
from .views.vault import VaultView


urlpatterns = [
    url(r'^registration', RegistrationView.as_view(), name=u'registration'),
    url(r'^vault/(?P<guid>[A-Za-z0-9-]+)', VaultView.as_view(), name=u'vault'),
    url(r'^$', AuthenticationView.as_view(), name=u'auth'),
    url(r'^chrome-extension/csrf-token', ChromeExtensionLoginView.as_view(), name=u'ce-csrf'),
    # url(r'^chrome-extension/registration', ChromeExtensionRegistrationView.as_view(), name=u'ce-registration'),
    # url(r'^chrome-extension/vault', ChromeExtensionVaultView.as_view(), name=u'ce-vault'),
]
