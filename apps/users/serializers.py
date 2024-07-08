from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["user_id"] = str(user.id)
        # token['email'] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
        )


class UserRegSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    # email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
