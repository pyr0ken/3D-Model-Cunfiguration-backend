from django.contrib import admin
from .models import Room, RoomMember, RoomModel


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("owner", "title", "is_active", "meeting_id", "created_at")


@admin.register(RoomModel)
class RoomModelAdmin(admin.ModelAdmin):
    list_display = ("room", "edit_model", "is_select", "created_at")


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "is_leave", "last_join")
