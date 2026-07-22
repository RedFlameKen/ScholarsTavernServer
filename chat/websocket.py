from datetime import datetime
from http.cookies import SimpleCookie
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from chat.controller import create_text_chat, get_channel_chats, verify_chat_channel_user


class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        headers = self.scope.get("headers")

        cookie = SimpleCookie()
        for header in headers:
            if header[0] == b"cookie":
                cookie.load(header[1].decode())

        if "user_id" not in cookie:
            print("user_id not in cookie")
            self.close()
            return

        self.user_id = cookie["user_id"].value

        self.chat_channel_id = self.scope.get("url_route", {})["kwargs"]["chat_channel_id"]

        verification_status = verify_chat_channel_user(
            user_id=int(self.user_id),
            chat_channel_id=int(self.chat_channel_id))

        if not verification_status.success:
            print("failed to verify user")
            self.close()
            return

        chat_channel = verification_status.data["channel"]

        self.room_group_name = f"chat_{chat_channel.pk}"

        chats = get_channel_chats(chat_channel_id=chat_channel.pk).data["chats"]

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.send(text_data=json.dumps({
            "type": "load_chats",
            "chats": chats
        }))

    def disconnect(self, code: int) -> None:
        if not hasattr(self, 'room_group_name'):
            return
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        if text_data is not None:
            data = json.loads(text_data)
            print(f"received: {data}")

            if data["type"] == "message_sent":
                chat_data = data["chat"]
                if chat_data["type"] == "text":
                    text = chat_data["text"]
                    time_sent = datetime.now()
                    sender_id = chat_data["sender"]
                    chat_channel_id = chat_data["chat_channel_id"]
                    create_status = create_text_chat(
                        text=text,
                        time_sent=time_sent,
                        sender_id=sender_id,
                        chat_channel_id=chat_channel_id
                    )

                    if not create_status.success:
                        return

                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            "type": "signal_message",
                            "data": {
                                "type": "message_sent",
                                "data": create_status.data
                            }
                        }
                    )

    def signal_message(self, event):
        print(event)
        self.send(text_data=json.dumps(event["data"]))
