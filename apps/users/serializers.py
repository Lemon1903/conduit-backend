from rest_framework import serializers

from ..authentication.models import User
from .models import Profile


# This is for route: # /profiles/<username>
class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["bio", "image", "followers"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["username"] = instance.user.username
        rep["email"] = instance.user.email
        return rep


# This is for route: # /user/
class ProfileViewUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", required=False)
    email = serializers.CharField(source="user.email", required=False)
    password = serializers.CharField(
        source="user.password",
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Profile
        fields = ["username", "email", "password", "bio", "image"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        # Update user fields if provided
        user = instance.user
        password = user_data.pop("password", None)

        if password is not None:
            user.set_password(password)

        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update profile fields if provided
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
