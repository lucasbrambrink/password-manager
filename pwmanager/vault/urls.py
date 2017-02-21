from django.conf.urls import url
from .views import VaultView, AuthenticationView, RegistrationView

urlpatterns = [
    url(r'^registration', RegistrationView.as_view(), name=u'registration'),
    url(r'^vault/(?P<user_name>[a-z0-9]+)', VaultView.as_view(), name=u'vault'),
    url(r'^', AuthenticationView.as_view(), name=u'auth'),
]
