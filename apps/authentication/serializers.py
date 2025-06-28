from django.contrib import auth
from tokenize import TokenError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    # TODO: I don't know if need more validation here for security?
    def validate(self, attrs):
        username: str = attrs.get("username", "")

        # Username validation
        if not username.isalnum():
            raise serializers.ValidationError(self.default_error_messages)

        return attrs

    def create(self, validated_data):
        # `create_user` would handle hashing and default behavior
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email: str = attrs.get("email", "")
        password: str = attrs.get("password", "")
        user = auth.authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid Credentials.")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled.")

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get("refresh", "")
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("Bad Token.")
