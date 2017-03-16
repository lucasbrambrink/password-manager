from rest_framework import serializers
from vault.models import VaultUser, Password, PasswordEntity, VaultException, Address


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


class PasswordSerializer(serializers.ModelSerializer):
    passwordentity_set = PasswordEntitySerializer(many=True,
                                                  read_only=True,
                                                  allow_null=True)

    class Meta:
        model = Password
        fields = ('id',
                  'domain_name',
                  'key',
                  'external_unique_identifier',
                  'passwordentity_set')


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = Address._meta.get_all_field_names()



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
    password_guid = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)






class PasswordCreateSerializer(serializers.Serializer):
    VaultException = VaultException
    password = serializers.CharField(max_length=255)
    domain_name = serializers.CharField(max_length=255)
    password_guid = serializers.CharField(max_length=255,
                                          allow_blank=True,
                                          allow_null=True)

    @staticmethod
    def create_or_update(*args):
        return Password.objects.create_password(*args)

    @staticmethod
    def delete(key):
        try:
            password = Password.objects\
                .get(key=key)
            password.soft_delete()
        except Password.DoesNotExist:
            pass


class PasswordValueSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255,
                                  allow_blank=True,
                                  allow_null=True)

