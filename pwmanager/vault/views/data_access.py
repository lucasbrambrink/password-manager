from django.shortcuts import redirect
from django.views.generic import View
from django.http import JsonResponse
from ..models import VaultUser, Password
from ..utils.cache import AuthCache
from ..utils.user import UserApi
from ..utils.crypt import InvalidSignature, InvalidToken
from ..utils.vault_api import VaultException
import logging
import json
from urllib import parse
from django.core import serializers
from .authentication import Authenticate

log = logging.getLogger(__name__)


class DataAccessResponse(object):

    def __init__(self, success=False, data=None):
        self.success = success
        self.data = data


class PasswordListView(View):

    def get(self, request, guid, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth')

        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return redirect('auth')

        Authenticate.store_nonce(request, nonce)
        vu = VaultUser.objects.get(guid=guid)
        passwords = vu.vault.password_set\
            .all()\
            .order_by('-created')\
            .only('domain_name', 'key')

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

        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
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
        access = UserApi(user.role_name, token, user_key)

        try:
            password = Password.objects.get(key=query)
        except Password.DoesNotExist:
            return self.return_none()

        try:
            value = access.read(query)
        except (InvalidSignature, InvalidToken, TypeError):
            value = None

        if not value:
            return self.return_none()

        Authenticate.store_nonce(request, nonce)
        return JsonResponse(DataAccessResponse(
            success=True,
            data={
                'value': value,
            }
        ).__dict__)


class DataAccessWrite(DataAccessView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.return_none()

        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return self.return_none()

        data = self.parse_json(request)
        if not data:
            return self.return_none()

        name = data.get('domainName')
        password = data.get('password')
        guid = data.get('guid')

        if None in (name, password, guid):
            return self.return_none()

        user = self.get_user(guid)
        if not user:
            return self.return_none()

        token = AuthCache.get_token(key)
        try:
            Password.objects.create_password(
                user, token, name, password, user_key
            )
        except VaultException:
            return self.return_none()

        Authenticate.store_nonce(request, nonce)
        return JsonResponse(DataAccessResponse(
            success=True,
            data={}
        ).__dict__)

