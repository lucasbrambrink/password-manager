from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from ..models import LoginAttempt
from ..forms import LoginForm
from ..utils.app_role import AppRoleApi
from ..utils.cache import AuthCache
from ..utils.tokens import TokenException
from ..utils.crypt import InvalidSignature, InvalidToken, SymmetricEncryption
from ..utils.mem_store import EncryptionStore
import logging
import datetime


log = logging.getLogger(__name__)


class Authenticate(object):
    """
    continuous exchange of nonce for new nonce
        * ensures no possible cross-interference
    """
    NONCE = u'nonce'
    SESSION_KEY = u'session-key'

    @classmethod
    def check_authentication(cls, request):
        if not request.user.is_authenticated:
            log.warning('Unauthenticated user request')
            return False, None, None, None

        try:
            nonce = request.session.pop('nonce')
        except KeyError:
            log.warning('Request without nonce')
            return False, None, None, None

        # check nonce and generate new one
        try:
            authenticated, nonce, key = AuthCache.digest_nonce(nonce)
            if not authenticated:
                log.warning('Unable to digest nonce')
                return False, None, None, None
        except (InvalidToken, InvalidSignature) as ex:
            log.warning('Unable to process nonce keys')
            return False, None, None, None

        try:
            user_key = SymmetricEncryption.decrypt(
                EncryptionStore.TRANSIENT_E_KEY,
                request.session[cls.SESSION_KEY])

        except (KeyError, InvalidSignature, InvalidToken) as ex:
            log.warning('Unable to retrieve user encryption key')
            return False, None, None, None


        # yield new nonce if last one was correct
        cls.store_nonce(request, nonce)
        return True, nonce, key, user_key

    @staticmethod
    def initialize_vault_access_token(user):
        app_role_api = AppRoleApi()
        token = app_role_api.get_user_access_token(user.role_name)
        if token is None:
            raise TokenException('Unable to obtain token...')
        # create key, store encrypted
        key = AuthCache.set_token(token)
        # nonce points to encrypted key
        nonce = AuthCache.set_nonce(key)
        return nonce



    @classmethod
    def initalize_nonce(cls, request, user):
        nonce = cls.initialize_vault_access_token(user)
        cls.store_nonce(request, nonce)

    @classmethod
    def login_user(cls, request, user, password):
        """
        add nonce to session store
        """
        encryption_key = SymmetricEncryption.build_encryption_key(password)
        # put this key in the cache for the user session
        request.session[cls.SESSION_KEY] = SymmetricEncryption.encrypt(
            EncryptionStore.TRANSIENT_E_KEY,
            encryption_key)

        cls.initalize_nonce(request, user)

    @classmethod
    def store_nonce(cls, request, nonce):
        request.session[cls.NONCE] = nonce


class LoginException(Exception):
    """unable to authenticate"""


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

        try:
            attempts = LoginAttempt.objects\
                .filter(email=email)\
                .filter(created__lte=datetime.datetime.now() - datetime.timedelta(hours=1))\
                .filter(success=False)\
                .count()
            if attempts > 3:
                raise LoginException(login_attempt.TOO_MANY_TRIES)

            if None in (email, password):
                raise LoginException(login_attempt.EMPTY)

            user = authenticate(email=email, password=password)

            if user is None:
                raise LoginException(login_attempt.WRONG)

            login(request, user)
            # mount to vault
            Authenticate.login_user(request, user, password)
            login_attempt.success = True
            login_attempt.save()
            return redirect(u'vault', guid=user.guid)
        except LoginException as ex:
            login_attempt.error_msg = ex
        except TokenException:
            login_attempt.error_msg = u'Unable to authenticate to security layer. ' \
                                      u'Our administrators are definitely freaking out right now.'

        login_attempt.save()
        return render(request, self.template_name, {
            'form': LoginForm(),
            'error': login_attempt.error_msg
        })


class ChromeExtensionLoginView(TemplateView):
    template_name = u'vault/components/csrf_token.html'

    def get(self, request, *args, **kwargs):
        """
        only allow 3 attempts
        perhaps perform some kind of MFA
        """
        # authenticate user
        # perhaps return json response?
        return render(request, self.template_name, {})
