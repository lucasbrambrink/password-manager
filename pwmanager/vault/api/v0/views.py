# from snippets.models import Snippet
from .serializers import PasswordSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, is_authenticated
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from .serializers import (
    AuthenticationSerializer,
    VaultUserSerializer,
    PasswordSerializer,
    PasswordValueSerializer,
    PasswordCreateSerializer)
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from django.contrib.auth import login, authenticate
from vault.views.authentication import Authenticate
from vault.views.authentication import AuthCache

import logging

log = logging.getLogger(__name__)


class AuthenticationView(generics.UpdateAPIView,
                         generics.GenericAPIView):
    authentication_classes = ()
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = AuthenticationSerializer

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        if not request.user or not is_authenticated(request.user):
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        Authenticate.initalize_nonce(request, request.user)
        return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = AuthenticationSerializer(data=request.data)
        user = None

        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data["email"],
                                password=serializer.validated_data["password"])

        if not user:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        token, created = Token.objects.get_or_create(user=user)
        Authenticate.login_user(request, user, serializer.validated_data["password"])
        return Response({'token': token.key})


class ProvisionNonceView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated)

    def put(self, request, *args, **kwargs):
        Authenticate.initalize_nonce(request, request.user)
        return Response({}, status=status.HTTP_200_OK)


class PasswordListView(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordSerializer

    def get_queryset(self):
        return self.request.user\
            .vault.password_set\
            .filter(is_active=True)

    def post(self, request, *args, **kwargs):
        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)
        return self.list(request, *args, **kwargs)


class PasswordView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordCreateSerializer

    def delete(self, request, *args, **kwargs):
        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        serializer = PasswordCreateSerializer(data=request.data)
        serializer.is_valid()
        serializer.delete(serializer.data.get("password_guid"))
        return Response({}, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        user = request.user
        token = AuthCache.get_token(key)
        serializer = PasswordCreateSerializer(data=request.data)

        success = False
        if serializer.is_valid():
            try:
                serializer.create_or_update(
                    user, token,
                    serializer.validated_data['domain_name'],
                    serializer.validated_data['password'],
                    user_key,
                    serializer.validated_data['password_guid']
                )
                success = True
            except serializer.VaultException:
                success = False

        if not success:
            return Response('Bad request. Sorry!',
                            status=status.HTTP_400_BAD_REQUEST)

        del serializer.validated_data['password']
        return Response(serializer.validated_data,
                        status=status.HTTP_201_CREATED)


class PasswordGetView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordSerializer

    def post(self, request, *args, **kwargs):
        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        user = request.user
        token = AuthCache.get_token(key)
        access = user.access_api(token, user_key)
        request.data["value"] = None
        serializer = PasswordValueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data["value"] = access.safe_read(serializer.data.get('query'))

        if not serializer.validated_data.get("value"):
            return Response('Bad request. Sorry!',
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data)

