from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from .serializers import LoginSerializer, RegisterSerializer


class RegisterApi(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            if User.objects.filter(username=username).exists():
                return Response(
                    {"detail": "نام کاربری در سیستم موجود میباشد."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            User.objects.create_user(username=username, password=password)

            return Response({"detail": "User created successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApi(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            user = authenticate(request, username=username, password=password)

            if not user:
                return Response({"detail": "کاربری با این مشخصات یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token, access_token = user.get_tokens()

            result = {
                "access_token": str(access_token),
                "refresh_token": str(refresh_token),
                "username": user.username,
                "user_id": str(user.id),
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
