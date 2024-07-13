import uuid
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
        An abstract base class model that provides
        self-updating ``created_at`` and ``updated_at`` and ``id`` fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
