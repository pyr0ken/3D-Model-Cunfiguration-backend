import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = "username"

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"
        ordering = ("-last_login",)

    def __str__(self) -> str:
        return f"{self.username}"

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return refresh, refresh.access_token

    def delete_token(self):
        return self.auth_token.delete()

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None) -> bool:
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label) -> bool:
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True
