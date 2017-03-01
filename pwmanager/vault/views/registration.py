from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from ..models import VaultUser
from ..forms import RegistrationForm
import logging
from django.db import IntegrityError
from .authentication import Authenticate

log = logging.getLogger(__name__)


class RegistrationView(TemplateView):
    template_name = u'vault/registration.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'error': '',
            'form': RegistrationForm()
        })

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        email = request.POST.get('email', None)
        if None in (username, password, email):
            error = 'Invalid params'

        else:
            try:
                vu = VaultUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                login(request, vu)
                Authenticate.login_user(request, vu)
                return redirect(u'vault', guid=vu.guid)
            except IntegrityError:
                error = u"That email exists already. Please log in or try another."

        return render(request, self.template_name, {
            'form': RegistrationForm(),
            'error': error
        })
