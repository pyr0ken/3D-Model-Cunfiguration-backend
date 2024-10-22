from django.db.models import IntegerChoices


class ModelStatusType(IntegerChoices):
    PUBLIC = 1, "Public"
    UPLOADED = 2, "Uploaded"
    CREATED_FROM_2D = 3, "Created From 2D"