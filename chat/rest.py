from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.room_group_name = "chat_room"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code: int) -> None:
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        message = ""

        if text_data is not None:
            json_message = json.loads(text_data)
            message = json_message['message']
            print(f"client said: {message}")

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": json_message["message"]
                }
            )

        self.send(text_data=json.dumps({
            'message': message
        }))

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "message": event["message"]
        }))
