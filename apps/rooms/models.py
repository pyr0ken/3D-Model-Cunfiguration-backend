from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.models.models import EditModel

class Room(BaseModel):
    title = models.CharField(max_length=255)
    meeting_id = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rooms"
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        db_table = "rooms"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.title} - {self.meeting_id} - {self.owner}"


class RoomMember(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_rooms"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_users")
    is_leave = models.BooleanField(default=False)
    last_join = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"
        db_table = "room_members"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user} - {self.room}"


class RoomModel(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_models")
    edit_model = models.ForeignKey(EditModel, on_delete=models.CASCADE, related_name="model_rooms")
    is_select = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Room Model"
        verbose_name_plural = "Room Models"
        db_table = "room_models"
        ordering = ("-created_at",)


    def __str__(self) -> str:
        return f"{self.room} - {self.edit_model}"
