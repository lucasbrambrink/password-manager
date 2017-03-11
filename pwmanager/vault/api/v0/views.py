# from snippets.models import Snippet
from .serializers import PasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from .serializers import VaultUserSerializer, PasswordSerializer, PasswordValueSerializer, PasswordCreateSerializer
from django.contrib.auth import login, logout
from vault.views.authentication import Authenticate
from vault.views.authentication import AuthCache

class AuthenticationView(generics.GenericAPIView):
    authentication_classes = (SessionAuthentication,)


    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(VaultUserSerializer(request.user).data)


class PasswordListView(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordSerializer

    def get_queryset(self):
        return self.request.user.vault.password_set.all()

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

    def update(self, request, *args, **kwargs):
        authenticated, nonce, key, user_key = Authenticate.check_authentication(request)
        if not authenticated:
            return Response(NotAuthenticated.default_detail.capitalize(),
                            status=NotAuthenticated.status_code)
        return self.create(request)

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
                        status=status.HTTP_202_ACCEPTED)


class PasswordGetView(generics.GenericAPIView):
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

