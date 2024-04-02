from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, *args, **kwargs):
        """
        Creates and saves a User with the given username,
        email and password.
        """
        if not username:
            raise ValueError("User most have an username.")

        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, *args, **kwargs):
        """
        Creates and saves a User with the given username,
        email and password.
        """
        user = self.create_user(
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
