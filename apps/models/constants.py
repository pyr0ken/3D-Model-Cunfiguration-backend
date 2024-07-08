from django.db.models import IntegerChoices


class ModelStatusType(IntegerChoices):
    PUBLIC = 1, "Public"
    UPLOADED = 2, "Uploaded"