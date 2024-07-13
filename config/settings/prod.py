from .base import *

# ------------------------ Logging Config ------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'django': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/djyoga/django-api.log',
        },
        'db': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/djyoga/django-db.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
