from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from ..models import VaultUser
from .authentication import Authenticate
import logging


log = logging.getLogger(__name__)




class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, guid, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return redirect('auth')

        vu = VaultUser.objects.get(guid=guid)
        return render(request, self.template_name, {
            u'user_name': vu.username,
            u'guid': vu.guid,
        })
