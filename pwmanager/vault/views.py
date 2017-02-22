from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from .models import LoginAttempt, VaultUser, PasswordEntity, Password
from .forms import LoginForm, RegistrationForm
from .utils import AppRoleApi, AuthCache, UserApi, GuidSource
import logging
import datetime
import json
from urllib import parse
from django.core import serializers


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

        try:
            nonce = request.session.pop('nonce')
        except KeyError:
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
            .filter(success=False)\
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
        })





class DataAccessResponse(object):

    def __init__(self, success=False, data=None):
        self.success = success
        self.data = data


class PasswordListView(View):

    def get(self, request, guid, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        authenticated, nonce, key = Authenticate.check_authentication(request)
        if not authenticated:
            return redirect('auth')

        Authenticate.store_nonce(request, nonce)
        vu = VaultUser.objects.get(guid=guid)
        passwords = vu.vault.password_set\
            .all()\
            .only('name', 'key')
        return JsonResponse(DataAccessResponse(
            success=True,
            data={
                'passwords': serializers.serialize('json', passwords)
            }
        ).__dict__)



class DataAccessView(View):
    """
    requires 2 nonces
    """

    def return_none(self):
        return JsonResponse(DataAccessResponse().__dict__)

    def parse_json(self, request):
        data = None
        try:
            decoded = parse.unquote(request.body.decode('utf-8'))
            data = json.loads(decoded)
        except ValueError:
            pass
        finally:
            return data

    def get_user(self, guid):
        user = None
        try:
            user = VaultUser.objects.get(guid=guid)
        except VaultUser.DoesNotExist:
            pass
        finally:
            return user



class DataAccessRead(DataAccessView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.return_none()

        authenticated, nonce, key = Authenticate.check_authentication(request)
        if not authenticated:
            return self.return_none()

        data = self.parse_json(request)
        if not data:
            return self.return_none()

        query = data.get('query')
        guid = data.get('guid')
        if None in (query, guid):
            return self.return_none()

        user = self.get_user(guid)
        if not user:
            return self.return_none()

        token = AuthCache.get_token(key)
        access = UserApi(user.role_name, token)

        try:
            password = Password.objects.get(key=query)
        except Password.DoesNotExist:
            return self.return_none()

        response = access.read(query)
        if not response:
            return self.return_none()

        Authenticate.store_nonce(request, nonce)
        return JsonResponse(DataAccessResponse(
            success=True,
            data={
                'value': response.get('value'),
            }
        ).__dict__)


class DataAccessWrite(DataAccessView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.return_none()

        authenticated, nonce, key = Authenticate.check_authentication(request)
        if not authenticated:
            return self.return_none()

        data = self.parse_json(request)
        if not data:
            return self.return_none()

        name = data.get('name')
        password = data.get('password')
        guid = data.get('guid')

        if None in (name, password, guid):
            return self.return_none()

        user = self.get_user(guid)
        if not user:
            return self.return_none()

        token = AuthCache.get_token(key)
        access = UserApi(user.role_name, token)

        password_guid = GuidSource.generate()
        success = access.write(password_guid, password)

        if not success:
            return self.return_none()

        # todo: move to obejct manager
        password = Password(
            name=name,
            vault=user.vault,
            key=password_guid
        )
        password.save()
        entity = PasswordEntity(
            guid=password_guid,
            password=password
        )
        entity.save()

        Authenticate.store_nonce(request, nonce)
        return JsonResponse(DataAccessResponse(
            success=True,
            data={}
        ).__dict__)



