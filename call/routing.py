from django.urls import re_path

from call.websocket import CallConsumer

call_websocket_urlpatterns = [
    re_path(r"^call/$", CallConsumer.as_asgi(),),
]
