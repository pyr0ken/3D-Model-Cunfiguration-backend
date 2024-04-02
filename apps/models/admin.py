from django.contrib import admin
from .models import Model, Point, Note


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "file", "created_at")
    list_filter = ("created_at", "updated_at")
    list_per_page = 50

    search_fields = (
        "title",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)

    filter_horizontal = []


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "position", "color", "created_at")
    list_filter = ("created_at", "updated_at")
    list_per_page = 50

    search_fields = (
        "position",
        "color",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)

    filter_horizontal = []


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "point", "created_at")
    list_filter = ("created_at", "updated_at")
    list_per_page = 50

    search_fields = (
        "title",
        "description",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)

    filter_horizontal = []
