from rest_framework import serializers
from vault.models import VaultUser, Password, PasswordEntity


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
    passwordentity_set = PasswordEntitySerializer(many=True, read_only=True)

    class Meta:
        model = Password
        fields = ('id', 'domain_name', 'key', 'passwordentity_set')

