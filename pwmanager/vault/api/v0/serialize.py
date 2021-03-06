from rest_framework import serializers
from vault.models import VaultUser, DomainName, ExternalAuthentication, PasswordEntity, VaultException, Address

import logging

log = logging.getLogger(__name__)


class AuthenticationSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class VaultUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultUser
        fields = ('id', 'username', 'email', 'linenos', 'language', 'style')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return VaultUser.objects.create(**validated_data)


class PasswordEntitySerializer(serializers.ModelSerializer):
    created_time = serializers.SerializerMethodField()

    def get_created_time(self, obj):
        created = obj.created
        return created.strftime("%B %d, %Y, %I:%M %p")

    class Meta:
        model = PasswordEntity
        fields = ('id', 'created', 'guid', 'created_time')



class ExternalAuthenticationSerializer(serializers.ModelSerializer):
    passwordentity_set = PasswordEntitySerializer(many=True,
                                                  read_only=True,
                                                  allow_null=True)

    class Meta:
        model = ExternalAuthentication
        fields = ('key',
                  'user_name',
                  'created',
                  'passwordentity_set')


class DomainNameSerializer(serializers.ModelSerializer):
    externalauthentication_set = ExternalAuthenticationSerializer(many=True,
                                                                  read_only=True,
                                                                  allow_null=True)

    class Meta:
        model = DomainName
        fields = ('domain_name',
                  'externalauthentication_set')


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = (
            'address1',
            'address2',
            'city',
            'state',
            'zip_code'
        )



class ProfileSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)
    email = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)
    phone_number = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)
    address = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)
    password_guid = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)






class PasswordCreateSerializer(serializers.Serializer):
    VaultException = VaultException
    password = serializers.CharField(max_length=255)
    domain_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    password_guid = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)

    def create(self, user, token, user_key):
        assert self.validated_data is not None
        DomainName.objects.create_or_update_password(
            user=user,
            token=token,
            domain_name=self.validated_data['domain_name'],
            username=self.validated_data['username'],
            password=self.validated_data['password'],
            user_key=user_key,
            password_guid=self.validated_data['password_guid']
        )


class PasswordDeleteSerializer(serializers.Serializer):
    domain_name = serializers.CharField(max_length=255)
    password_guid = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)

    @staticmethod
    def delete(user, domain_name, key):
        try:
            password = ExternalAuthentication.published\
                .get(key=key)
            password.soft_delete()
        except ExternalAuthentication.DoesNotExist:
            log.warning("Unable to find auth object from key: %s" % key)

        try:
            domain = user.vault.domainname_set\
                .get(domain_name=domain_name)
            if not domain.externalauthentication_set\
                    .filter(is_active=True).count():
                domain.soft_delete()
        except DomainName.DoesNotExist:
            log.warning("Unable to find domain name domain name: %s" % domain_name)




class PasswordValueSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255,
                                  allow_blank=True,
                                  allow_null=True)

