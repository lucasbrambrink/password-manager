from django.conf.urls import url
# from .views import
from rest_framework.authtoken import views
from .views import DomainNameListView, PasswordGetView, DomainNameView, AuthenticationView, ProvisionNonceView

urlpatterns = [
    url(r'^auth/get-token/', AuthenticationView.as_view()),
    url(r'^auth/get-nonce/', ProvisionNonceView.as_view()),
    url(r'^password/$',
        PasswordGetView.as_view(),
        name=u'password'),
    url(r'^password/create/$',
        DomainNameView.as_view(),
        name=u'password-create'),
    url(r'^password/list/$',
        DomainNameListView.as_view(),
        name=u'password-list'),
]
