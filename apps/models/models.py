from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import BaseModel


class Model(BaseModel):
    title = models.CharField()
    file = models.FileField(upload_to="models")

    class Meta:
        verbose_name = "Model"
        verbose_name_plural = "Models"
        db_table = "models"

    def __str__(self) -> str:
        return f"{self.file.name}"


class Point(BaseModel):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="points")
    position =  ArrayField(models.FloatField(), size=3)
    color = models.CharField()

    class Meta:
        verbose_name = "Point"
        verbose_name_plural = "Points"
        db_table = "points"

    def __str__(self) -> str:
        return f"{self.position} - {self.color}"


class Note(BaseModel):
    point = models.ForeignKey(Point, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField()
    description = models.TextField()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        db_table = "notes"

    def __str__(self) -> str:
        return f"{self.title}"
