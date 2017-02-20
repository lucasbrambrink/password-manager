from django.conf.urls import url
from .views import VaultView, AuthenticationView

urlpatterns = [
    url(r'^', AuthenticationView.as_view(), name=u'auth'),
    url(r'^vault/(?P<user_name>[a-z0-9]+)', VaultView.as_view(), name=u'vault')
]
