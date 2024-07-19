from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from .serializers import LoginSerializer, RegisterSerializer


class RegisterApi(APIView):
    """
    API endpoint for user registration.
    """

    def post(self, request):
        """
        Register a new user.
        """
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                return Response(
                    {"detail": "نام کاربری در سیستم موجود میباشد."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a new user
            User.objects.create_user(username=username, password=password)

            return Response({"detail": "User created successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApi(APIView):
    """
    API endpoint for user login.
    """

    def post(self, request):
        """
        Authenticate a user and provide access and refresh tokens.
        """
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if not user:
                return Response({"detail": "کاربری با این مشخصات یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate tokens
            refresh_token, access_token = user.get_tokens()

            result = {
                "access_token": str(access_token),
                "refresh_token": str(refresh_token),
                "username": user.username,
                "user_id": str(user.id),
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
