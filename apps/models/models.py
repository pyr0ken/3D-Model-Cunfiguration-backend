from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.core.models import BaseModel
from .constants import ModelStatusType


class Model(BaseModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="models"
    )
    title = models.CharField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=ModelStatusType.choices)
    file = models.FileField(
        upload_to="models",
        validators=[
            FileExtensionValidator(
                [
                    "glb",
                    "gltf",
                ]
            )
        ],
    )

    class Meta:
        verbose_name = "Model"
        verbose_name_plural = "Models"
        db_table = "models"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} - {self.file.name}"


class EditModel(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_models"
    )
    model = models.ForeignKey(
        Model, on_delete=models.CASCADE, related_name="user_models"
    )
    display_name = models.CharField(max_length=255)
    last_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Edit Model"
        verbose_name_plural = "Edit Models"
        db_table = "edit_models"

    def __str__(self) -> str:
        return f"{self.user} - {self.display_name}"


class Point(BaseModel):
    edit_model = models.ForeignKey(
        EditModel, on_delete=models.CASCADE, related_name="edit_model_points")
    position = models.CharField()
    color = models.CharField()
    radius = models.FloatField()
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Point"
        verbose_name_plural = "Points"
        db_table = "points"

    def __str__(self) -> str:
        return f"{self.position} - {self.color}"
