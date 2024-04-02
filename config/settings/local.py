from .base import *

# ------------------------ Application definition ------------------------
MIDDLEWARE += [
    "silk.middleware.SilkyMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += [
    "silk",
    "debug_toolbar",
]

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
