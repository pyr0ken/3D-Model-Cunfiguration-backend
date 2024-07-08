import json
import urllib
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.rooms.models import Room, RoomMember, Chat
from apps.rooms.serializers import RoomMembersSerializer
from .speech_to_text import transcribe_audio

User = get_user_model()


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user_cookie = self.scope["cookies"]["user"]

        self.user_id = self.get_user_id()
        self.room = await self.get_room()
        self.room_group_name = "room_%s" % self.room_id

        await self.add_user_to_room()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Firing signals to other user about user who just disconneted
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "disconnected",
                "data": {"from": self.user_id},
            },
        )
        await self.remove_user_from_room()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data["type"] == "new_user_joined":
            # All the users is notified about new user joining
            data["members"] = await self.get_room_members()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_user_joined",
                    "data": data,
                },
            )

        # Offer from the user is send back to other users in the room
        elif data["type"] == "sending_offer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "sending_offer",
                    "data": data,
                },
            )

        # Answer from the user is send back to user who sent the offer
        elif data["type"] == "sending_answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "sending_answer",
                    "data": data,
                },
            )

        # Firing signals to other user about user who just disconneted
        elif data["type"] == "disconnected":
            # data["userName"] = self.get_username()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "disconnected",
                    "data": data,
                },
            )

    # FUNCTIONS FOR THE GROUP SEND METHOD ABOVE...
    async def new_user_joined(self, event):
        data = event["data"]
        await self.send(
            json.dumps(
                {
                    "type": "new_user_joined",
                    "members": data["members"],
                    "from": data["from"],
                }
            )
        )

    async def sending_offer(self, event):
        data = event["data"]
        await self.send(
            json.dumps(
                {
                    "type": "sending_offer",
                    "from": data["from"],
                    "to": data["to"],
                    "offer": data["offer"],
                }
            )
        )

    async def sending_answer(self, event):
        data = event["data"]
        await self.send(
            json.dumps(
                {
                    "type": "sending_answer",
                    "from": data["from"],
                    "to": data["to"],
                    "answer": data["answer"],
                }
            )
        )

    async def disconnected(self, event):
        data = event["data"]
        await self.send(
            json.dumps(
                {
                    "type": "disconnected",
                    "from": data["from"],
                }
            )
        )

    def get_user_id(self):
        decoded_str = urllib.parse.unquote(self.user_cookie)
        json_data = json.loads(decoded_str)
        return json_data["userId"]

    # def get_username(self):
    #     decoded_str = urllib.parse.unquote(self.user_cookie)
    #     json_data = json.loads(decoded_str)
    #     return json_data["username"]

    @database_sync_to_async
    def get_room(self):
        try:
            room = Room.objects.get(room_id=self.room_id)
            return room
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def add_user_to_room(self):
        if self.room:
            member, created = RoomMember.objects.get_or_create(
                user_id=self.user_id, room_id=self.room.id
            )
            member.is_leave = False
            member.save(update_fields=["is_leave"])
            return member
        return None

    @database_sync_to_async
    def remove_user_from_room(self):
        member = RoomMember.objects.filter(
            user_id=self.user_id, room_id=self.room.id
        ).first()
        if member:
            member.is_leave = True
            member.save(update_fields=["is_leave", "last_join"])
            return member
        return None

    @database_sync_to_async
    def get_room_members(self):
        if self.room:
            members = RoomMember.objects.filter(room_id=self.room.id)
            serializer = RoomMembersSerializer(members, many=True)
            return serializer.data
        return None


class SpeechToTextConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            transcript = transcribe_audio(bytes_data)
            await self.send(text_data=json.dumps({"transcript": transcript}))
