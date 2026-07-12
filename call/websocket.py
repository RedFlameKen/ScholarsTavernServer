from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import WebsocketConsumer

from http.cookies import SimpleCookie

rooms = {}


class CallConsumer(WebsocketConsumer):
    def connect(self) -> None:
        headers = self.scope.get("headers")

        cookie = SimpleCookie()
        for header in headers:
            if header[0] == b"cookie":
                cookie.load(header[1].decode())

        if "user_id" not in cookie:
            self.close()
            return

        self.user_id = cookie["user_id"].value
        self.room_group_name = "call_room"

        room = rooms.setdefault(self.room_group_name, {})
        room[int(self.user_id)] = self.channel_name

        existing_users = list(room.keys())
        print(f"existing users: {existing_users}")

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.send(text_data=json.dumps({
            "type": "existing_users",
            "users": existing_users
        }))

    def disconnect(self, code: int) -> None:
        room = rooms.get(self.room_group_name)

        if room:
            room.pop(int(self.user_id), None)

            if not room:
                rooms.pop(self.room_group_name)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "user_left",
                "user_id": int(self.user_id),
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        if text_data is not None:
            data = json.loads(text_data)
            print(f"received: {data}")
            print(f"rooms: {rooms}")
            room = rooms[self.room_group_name]

            target = room[data["to"]]

            async_to_sync(self.channel_layer.send)(
                target,
                {
                    "type": "signal_message",
                    "user_id": int(self.user_id),
                    "sender": self.channel_name,
                    "data": data
                }
            )

    def user_left(self, event):
        self.send(text_data=json.dumps({
            "type": "user_left",
            "user_id": event["user_id"]
        }))

    def signal_message(self, event):
        if event["sender"] == self.channel_name:
            return

        print(f"signaling message: {event}")

        event["data"]["from"] = event["user_id"]

        self.send(text_data=json.dumps(event["data"]))
