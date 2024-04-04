from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.models import User
from .serializers import UserRegSerializer, MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["POST"])
def user_registration(request):
    serializer = UserRegSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "username is already exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(username=username, password=password)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
