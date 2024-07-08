"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.websocket import routing as echo_routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django_application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AuthMiddlewareStack(URLRouter(echo_routing.websocket_urlpatterns)),
    }
)
