from django.urls import re_path

from call.websocket import CallConsumer

websocket_urlpatterns = [
    re_path(r"^call/$", CallConsumer.as_asgi(),),
]
