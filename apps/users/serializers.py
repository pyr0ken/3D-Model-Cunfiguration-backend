from rest_framework import serializers
from .models import User

class AuthBaseSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class RegisterSerializer(AuthBaseSerializer):
    ...


class LoginSerializer(AuthBaseSerializer):
    ...

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
        )
