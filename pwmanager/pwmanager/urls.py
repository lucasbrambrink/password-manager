from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v0/', include('vault.api.v0.urls')),
    url(r'^', include(u'vault.urls')),
    # url(r'', include('two_factor.urls', 'two_factor')),
]
