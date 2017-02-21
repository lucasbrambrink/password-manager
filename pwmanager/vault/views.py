from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import LoginAttempt, VaultUser
from .forms import LoginForm, RegistrationForm
import logging
import datetime

log = logging.getLogger(__name__)


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
        return render(request, self.template_name, {
            'error': '',
            'form': LoginForm()
        })

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        login_attempt = LoginAttempt(email=email)

        attempts = LoginAttempt.objects\
            .filter(email=email)\
            .filter(created__lte=datetime.datetime.now() - datetime.timedelta(hours=1))\
            .count()
        if attempts > 3:
            login_attempt.success = False
            login_attempt.error_msg = login_attempt.TOO_MANY_TRIES
        elif None in (email, password):
            login_attempt.success = False
            login_attempt.error_msg = login_attempt.EMPTY

        else:
            user = authenticate(email=email, password=password)
            if user is None:
                login_attempt.success = False
                login_attempt.error_msg = login_attempt.WRONG

            else:
                login(request, user)
                login_attempt.success = True
                login_attempt.save()
                return redirect(u'vault', user_name=user.username)

        login_attempt.save()
        return render(request, self.template_name, {
            'form': LoginForm(),
            'error': login_attempt.error_msg
        })


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
            # try:
            vu = VaultUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, vu)
            return redirect(u'vault', user_name=vu.username)
            # except Exception as exc:
            #     error = u'Unable to register.. Sorry!'
            #     log.warning(msg=exc)

        return render(request, self.template_name, {
            'form': RegistrationForm(),
            'error': error
        })





class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        return render(request, self.template_name, {
            u'passwords': []
        })


