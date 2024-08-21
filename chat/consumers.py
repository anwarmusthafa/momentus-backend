import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import CustomUser
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract user ID from the WebSocket scope or authentication
        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

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

        sender_info = await self.get_user_info_by_id(sender_id)
        print("sender_info ",sender_info, "self.user_id",self.user_id, "sender_id", sender_id) 

        # Send message to room group if not from the current user
        if sender_id != sender_info['id']:
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
