from django.conf.urls import url
from .views import VaultView, AuthenticationView, RegistrationView, Authenticate, DataAccessView

urlpatterns = [
    url(r'^registration', RegistrationView.as_view(), name=u'registration'),
    url(r'^vault/(?P<guid>[A-Za-z0-9-]+)', VaultView.as_view(), name=u'vault'),
    # url(r'^auth/request-nonce', Authenticate.as_view(), name='request-access'),
    url(r'^auth/data', DataAccessView.as_view(), name=u'secure-get'),
    url(r'^', AuthenticationView.as_view(), name=u'auth'),
]
