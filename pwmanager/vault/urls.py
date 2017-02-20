from django.conf.urls import url
from .views import VaultView

urlpatterns = [
    url(r'^', VaultView.as_view(), name=u'vault'),
]
