import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from asgiref.sync import sync_to_async

from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # room name url se lena
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Only allow authenticated users
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # group join
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # group leave
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # message received from websocket client
    async def receive(self, text_data):
        user = self.scope["user"]
        data = json.loads(text_data or "{}")
        # frontend may send "text" (recommended) or "message" (legacy)
        text = (data.get("text") or data.get("message") or "").strip()
        if not text:
            return

        # Persist message
        room = await self._get_room(self.room_id)
        msg = await self._create_message(room=room, sender=user, text=text)

        # broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": msg.id,
                    "room_id": room.room_id,
                    "text": msg.text,
                    "sender_id": user.id,
                    "sender_username": user.username,
                    "timestamp_iso": msg.timestamp.isoformat(),
                },
            }
        )

    # message received from group_send
    async def chat_message(self, event):
        message = event["message"]

        # send to websocket client
        await self.send(text_data=json.dumps({
            "message": message
        }))

    @sync_to_async
    def _get_room(self, room_id: str) -> ChatRoom:
        return ChatRoom.objects.get(room_id=room_id)

    @sync_to_async
    def _create_message(self, room: ChatRoom, sender, text: str) -> Message:
        # Use model default timestamp (auto_now_add); keep timezone import in case you later want edits
        _ = timezone.now()
        return Message.objects.create(room=room, sender=sender, text=text)