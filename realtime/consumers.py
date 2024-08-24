from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import CustomUser
from channels.db import database_sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract user from scope (set by the JWTAuthMiddleware)
        self.user = self.scope['user']
        print(self.user, "user")

        # If user is authenticated, allow WebSocket connection
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        sender_id = text_data_json.get('sender')

        # If the sender is the current user, don't send the message back to them
        if sender_id == self.user.id:
            return  # Ignore the message sent by the user

        sender_info = await self.get_user_info_by_id(sender_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_info
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def get_user_info_by_id(self, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            return {
                'id': user.id,
                'username': user.momentus_user_name,
                'profile_picture': user.profile_picture.url if user.profile_picture else '',
            }
        except CustomUser.DoesNotExist:
            return {
                'username': 'Unknown',
                'profile_picture': ''
            }
