from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterApi.as_view(), name="user-registration"),
    path("login/", views.LoginApi.as_view(), name="user-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
