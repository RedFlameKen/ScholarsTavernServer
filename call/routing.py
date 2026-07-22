from django.urls import path

from call.websocket import CallConsumer

call_websocket_urlpatterns = [
    path("call/<int:group_id>/<int:call_channel_id>", CallConsumer.as_asgi(),),
]
