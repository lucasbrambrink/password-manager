from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse
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
                vaulted = VaultUser.authenticate_to_vault(user.guid)
                if not vaulted:
                    login_attempt.success = False
                    login_attempt.error_msg = login_attempt.UNABLE_TO_MOUNT
                else:
                    login_attempt.success = True
                    login_attempt.save()
                    return redirect(u'vault', user_name=user.guid)

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
            vaulted = VaultUser.authenticate_to_vault(vu.guid)
            if not vaulted:
                raise Exception('Unable to connect to Vault. Misconfigured')

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

    def get(self, request, user_name, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        vu = VaultUser.objects.get(guid=user_name)
        return render(request, self.template_name, {
            u'user_name': vu.username,
            u'guid': vu.guid,
            u'nonce': vu.hashed_nonce,
            u'passwords': []
        })


class Authenticate(View):
    """
    requires 1 nonce to yield 2nd one
    """

    def return_none(self):
        return JsonResponse({'data': None, 'success': False})

    @staticmethod
    def authenticate(self, request):
        if not request.user.is_authenticated:
            return False, None

        guid = request.POST.get('guid')
        nonce = request.POST.get('nonce')

        if None in (guid, nonce):
            return False, None

        try:
            vu = VaultUser.objects.get(guid=guid)
        except VaultUser.DoesNotExist:
            return False, None

        authenticated = vu.match_first_nonce(nonce)
        if not authenticated:
            return False, None

        return True, vu

    def post(self, request, *args, **kwargs):
        is_authenticated, user = self.authenticate(request)
        if not is_authenticated:
            return self.return_none()

        user.set_second_nonce()
        return JsonResponse({
            'success': True,
            'data': {
                'nonce': user.first_hash,
                'guid': user.guid,
                'second_nonce': user.second_hash,
            }
        })


class DataAccessView(View):
    """
    requires 2 nonces
    """
    def return_none(self):
        return JsonResponse({'data': None, 'success': False})

    def post(self, request, *args, **kwargs):
        key = request.POST.get('key')
        is_authenticated, user = Authenticate.authenticate(request)
        if not is_authenticated or key is None:
            return self.return_none()

        second_nonce = request.POST.get('second_nonce')
        is_authenticated = user.match_second_nonce(second_nonce)
        if not is_authenticated:
            return self.return_none()

        access = user.get_authenticated_access()
        response = access.read(key)

        # reset nonce per access
        user.set_nonce(True)
        return JsonResponse({
            'success': True,
            'data': {
                'nonce': user.first_hash,
                'value': response,
            }})







