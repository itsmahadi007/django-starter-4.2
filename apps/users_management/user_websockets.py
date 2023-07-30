import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationBase(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def user_update(self, event):
        await self.send(text_data=json.dumps(event["content"]))


class UserUpdateSocket(NotificationBase):
    async def connect(self):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        # print("&&&&&&&&&&&&&&&&&&&user_id", user_id)
        # self.room_name = self.scope["url_route"]["kwargs"]["company_id"]
        # self.room_group_name = "user_update_%s" % self.room_name
        self.room_group_name = "user_update"
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        elif int(user_id) == int(self.user.id):
            await super().connect()
        else:
            await self.close()
