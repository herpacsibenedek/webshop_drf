from rest_auth.serializers import LoginSerializer
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'last_login', 'date_joined']
        read_only_fields = ('id', 'last_login', 'date_joined', 'email')


class RegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save(update_fields=['first_name', 'last_name'])


class LoginSerializer(LoginSerializer):
    username = None
