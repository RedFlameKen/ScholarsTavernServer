"""
ASGI config for ScholarsTavernServer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from call.routing import call_websocket_urlpatterns
from chat.routing import chat_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ScholarsTavernServer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        call_websocket_urlpatterns + chat_websocket_urlpatterns  # type: ignore
    ),
})
