from django.conf.urls import url
# from .views import
from rest_framework.authtoken import views
from .views import PasswordListView, PasswordGetView, PasswordView
# urlpatterns += [
# ]
urlpatterns = [
    # url(r'^auth/get-token/', views.obtain_auth_token),
    url(r'^password/$',
        PasswordGetView.as_view(),
        name=u'password'),
    url(r'^password/create/$',
        PasswordView.as_view(),
        name=u'password-create'),
    url(r'^password/list/$',
        PasswordListView.as_view(),
        name=u'password-list'),
    # url(r'^auth/data/create', PasswordView.as_view(), name=u'secure-write'),
    # url(r'^auth/login'),
    # url(r'^authenticate', AuthenticationView.)
    # url(r'^registration', RegistrationView.as_view(), name=u'registration'),
    # url(r'^vault/(?P<guid>[A-Za-z0-9-]+)/list', PasswordListView.as_view(), name=u'vault-list'),
    # url(r'^vault/(?P<guid>[A-Za-z0-9-]+)', VaultView.as_view(), name=u'vault'),
    # # url(r'^auth/request-nonce', Authenticate.as_view(), name='request-access'),
    # url(r'^auth/data/get', DataAccessRead.as_view(), name=u'secure-get'),
    # url(r'^auth/data/create', DataAccessWrite.as_view(), name=u'secure-write'),
    # url(r'^', AuthenticationView.as_view(), name=u'auth'),
]
