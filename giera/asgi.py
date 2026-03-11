"""
ASGI config for giera project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

# use settings from file settings.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "giera.settings")

# handling requests HTTP (GET, POST, ...)
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from base.routing import websocket_urlpatterns

# take protocol and spread between Django (HTTP) and Channels (WebSocket)
application = ProtocolTypeRouter({
    "http": django_asgi_app,

    # add django authorization for websocket
    "websocket": AuthMiddlewareStack(
        # add routes from routing.py for websocket
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
