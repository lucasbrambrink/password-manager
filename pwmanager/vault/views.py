from django.shortcuts import render
from django.views.generic import TemplateView


class AuthenticationView(TemplateView):
    template_name = u'vault/authentication.html'

    def get(self, request, *args, **kwargs):
        """
        only allow 3 attempts
        perhaps perform some kind of MFA
        """
        # authenticate user
        # perhaps return json response?
        pass


class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            u'passwords': []
        })


