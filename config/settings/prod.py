from .base import *

# ------------------------ Application definition ------------------------
ADMINS = [
    ('', ''),
]

# ------------------------ Redis Config ------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config("REDIS_LOCATION", default="redis://127.0.0.1:6379"),
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": config("REDIS_PASSWORD"),
        }
    }
}

# ------------------------ Celery Config ------------------------
CELERY_BROKER_URL = f'redis://:{config("REDIS_PASSWORD")}@127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# ------------------------ Logging Config ------------------------
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'django': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/djyoga/django-api.log',
#         },
#         'db': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/djyoga/django-db.log',
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['django', 'mail_admins'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'django.db.backends': {
#             'handlers': ['db'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     }
# }
