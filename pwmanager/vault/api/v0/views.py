# from snippets.models import Snippet
from .serializers import PasswordSerializer
from rest_framework import mixins
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from .serializers import VaultUserSerializer, PasswordSerializer
from django.contrib.auth import login, logout
from vault.models import Password



class AuthenticationView(generics.GenericAPIView):
    authentication_classes = (SessionAuthentication,)

    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(VaultUserSerializer(request.user).data)


class PasswordList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    queryset = Password.objects.all()
    serializer_class = PasswordSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# class PasswordLookup(generics.GenericAPIView):
#
#     def get(self):
#         pass