# from snippets.models import Snippet
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
    DomainNameSerializer,
    ExternalAuthenticationSerializer,
    PasswordValueSerializer,
    PasswordCreateSerializer,
    PasswordDeleteSerializer)
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
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        Authenticate.initialize_nonce(request, request.user)
        return Response({}, status=status.HTTP_200_OK)


class DomainNameListView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,
                              SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = DomainNameSerializer

    def get_queryset(self):
        return self.request.user\
            .vault.domainname_set\
            .filter(is_active=True)

    def post(self, request, *args, **kwargs):
        auth = Authenticate.check_authentication(request)
        if not auth.is_authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)
        return self.list(request, *args, **kwargs)


class DomainNameView(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordCreateSerializer

    def delete(self, request, *args, **kwargs):
        auth = Authenticate.check_authentication(request)
        if not auth.is_authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        serializer = PasswordDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response('Bad request. Sorry!',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.delete(user=request.user,
                          domain_name=serializer.validated_data.get("domain_name"),
                          key=serializer.validated_data.get("password_guid"))
        return Response({}, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        auth = Authenticate.check_authentication(request)
        if not auth.is_authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        user = request.user
        token = AuthCache.get_token(auth.key)
        serializer = PasswordCreateSerializer(data=request.data)
        print(serializer.__dict__)
        success = False
        if serializer.is_valid():
            try:
                serializer.create(user, token, auth.user_key)
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

    def post(self, request, *args, **kwargs):
        auth = Authenticate.check_authentication(request)
        if not auth.is_authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)

        user = request.user
        token = AuthCache.get_token(auth.key)
        access = user.access_api(token, auth.user_key)
        request.data["value"] = None
        serializer = PasswordValueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data["value"] = access.safe_read(serializer.data.get('query'))

        if not serializer.validated_data.get("value"):
            return Response('Bad request. Sorry!',
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data)

