from django.shortcuts import render
from django.views.generic import TemplateView
from .models import LoginAttempt
from .forms import LoginForm


class AuthenticationView(TemplateView):
    template_name = u'vault/authentication.html'

    def __init__(self, *args, **kwargs):
        super(AuthenticationView, self).__init__(*args, **kwargs)
        self.attempts = []

    def get(self, request, *args, **kwargs):
        """
        only allow 3 attempts
        perhaps perform some kind of MFA
        """
        # authenticate user
        # perhaps return json response?
        return render(request, {
            'form': LoginForm()
        })

    def post(self, request, *args, **kwargs):
        login = LoginAttempt()
        pass



class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            u'passwords': []
        })


