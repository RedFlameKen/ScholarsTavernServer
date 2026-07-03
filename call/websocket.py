from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import WebsocketConsumer


class CallConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.room_group_name = "call_room"

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
        if text_data is not None:
            data = json.loads(text_data)
            print(f"received: {text_data}")

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "sender": self.channel_name,
                    "data": data
                }
            )

    def signal_message(self, event):
        if event["sender"] == self.channel_name:
            return
        self.send(text_data=json.dumps(event["data"]))
