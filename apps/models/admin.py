from django.contrib import admin
from .models import Model, Point, EditModel


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = (
        "created_by",
        "title",
        "file",
        "get_status",
        "get_file_size",
        "get_file_format",
        "created_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    list_per_page = 50

    search_fields = (
        "title",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)

    filter_horizontal = []

    def get_file_size(self, obj):
        return f"{round(obj.file.size / (1024**2), 2)} MB"

    def get_file_format(self, obj):
        return obj.file.name.split(".")[-1]

    def get_status(self, obj):
        return obj.get_status_display()

    get_file_size.short_description = "Size"
    get_file_format.short_description = "Format"
    get_file_size.short_description = "Status"


@admin.register(EditModel)
class EditModelAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "model",
        "display_name",
        "get_file_size",
        "get_file_format",
        "created_at",
    )
    list_filter = ("created_at", "updated_at")
    list_per_page = 50

    search_fields = (
        "user__username",
        "model__title",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "id")
    ordering = ("-created_at",)

    filter_horizontal = []

    def get_file_size(self, obj):
        return f"{round(obj.model.file.size / (1024**2), 2)} MB"

    def get_file_format(self, obj):
        return obj.model.file.name.split(".")[-1]

    get_file_size.short_description = "Size"
    get_file_format.short_description = "Format"


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "note", "position",
                    "color", "image", "created_at")
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
