from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from .models import LoginAttempt, VaultUser
from .forms import LoginForm, RegistrationForm
from .utils import AppRoleApi, AuthCache, UserApi
import logging
import datetime

log = logging.getLogger(__name__)


class Authenticate(object):
    """
    continuous exchange of nonce for new nonce
        * ensures no possible cross-interference
    """
    NONCE = u'nonce'

    @staticmethod
    def check_authentication(request):
        if not request.user.is_authenticated:
            return False, None, None

        nonce = request.session.pop('nonce')
        if not nonce:
            return False, None, None

        # check nonce and generate new one
        authenticated, nonce, key = AuthCache.digest_nonce(nonce)
        if not authenticated:
            return False, None, None

        # yield new nonce if last one was correct
        return True, nonce, key

    @staticmethod
    def initialize_vault_access_token(user):
        app_role_api = AppRoleApi()
        token = app_role_api.get_user_access_token(user.role_name)
        nonce = None
        if token is not None:
            # create key, store encrypted
            key = AuthCache.set_token(token)
            # nonce points to encrypted key
            nonce = AuthCache.set_nonce(key)

        return nonce

    @classmethod
    def login_user(cls, request, user):
        """
        add nonce to session store
        """
        nonce = cls.initialize_vault_access_token(user)
        cls.store_nonce(request, nonce)

    @classmethod
    def store_nonce(cls, request, nonce):
        request.session[cls.NONCE] = nonce


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
                # mount to vault
                Authenticate.login_user(request, user)
                login_attempt.success = True
                login_attempt.save()
                return redirect(u'vault', guid=user.guid)

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
            Authenticate.login_user(request, vu)
            return redirect(u'vault', user_name=vu.username)

        return render(request, self.template_name, {
            'form': RegistrationForm(),
            'error': error
        })


class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, guid, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        authenticated, nonce, key = Authenticate.check_authentication(request)
        if not authenticated:
            return redirect('auth')

        Authenticate.store_nonce(request, nonce)
        vu = VaultUser.objects.get(guid=guid)
        print(nonce)
        return render(request, self.template_name, {
            u'user_name': vu.username,
            u'guid': vu.guid,
            u'passwords': []
        })


class DataAccessView(View):
    """
    requires 2 nonces
    """

    def return_none(self):
        return JsonResponse({
            'data': None,
            'success': False
        })

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.return_none()

        authenticated, nonce, key = Authenticate.check_authentication(request)
        if not authenticated:
            return self.return_none()

        query = request.POST.get('query')
        guid = request.POST.get('guid')
        if None in (query, guid):
            return self.return_none()

        try:
            user = VaultUser.objects.get(guid=guid)
        except VaultUser.DoesNotExist:
            return self.return_none()

        token = AuthCache.get_token(key)
        access = UserApi(user.role_name, token)
        response = access.read(query)

        Authenticate.store_nonce(nonce)
        return JsonResponse({
            'success': True,
            'data': {
                'value': response,
            }
        })







