from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from ..models import VaultUser
from .authentication import Authenticate
import logging


log = logging.getLogger(__name__)


class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, guid, *args, **kwargs):
        auth = Authenticate.check_authentication(request)
        if not auth.is_authenticated:
            return redirect('auth')

        vu = VaultUser.objects.get(guid=guid)
        return render(request, self.template_name, {
            u'user_name': vu.username,
        })
