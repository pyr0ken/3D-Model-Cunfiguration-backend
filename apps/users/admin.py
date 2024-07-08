from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserChangeForm, UserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("id", "username", "is_active", "last_login", "date_joined")
    list_filter = ("is_active", "is_admin", "date_joined", "last_login")
    list_per_page = 50

    search_fields = (
        "username",
        "date_joined",
        "last_login",
    )
    readonly_fields = ("date_joined", "last_login", "id")
    ordering = ("-last_login",)

    fieldsets = [
        (
            "Personal info",
            {"fields": ("username", "password", "id")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_admin", "is_superuser")},
        ),
        (
            "Authorization",
            {"fields": ("date_joined", "last_login")},
        ),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "username",
                    "password1",
                    "password2",
                ],
            },
        ),
    ]

    filter_horizontal = []
