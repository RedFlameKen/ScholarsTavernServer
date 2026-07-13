from django.urls import path

from chat.websocket import ChatConsumer

chat_websocket_urlpatterns = [
    path("chat/<int:chat_channel_id>", ChatConsumer.as_asgi(),),
]
