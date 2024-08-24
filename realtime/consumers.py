from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import CustomUser
from channels.db import database_sync_to_async
from realtime.models import ChatRoom, ChatMessage  # Import your models
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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
        message = text_data_json.get('message',)
        sender_id = text_data_json.get('sender')
        chat_room_id = self.room_id

        print(f"Received message: {message} {sender_id} {chat_room_id}")

        # If the sender is the current user, don't send the message back to them
        sender_info = await self.get_user_info_by_id(sender_id)
        saved_message = await self.save_message_to_db(chat_room_id, sender_id, message)
        if sender_id == self.user.id:
            return  # Ignore the message sent by the user

        # Get sender info and save the message to the database
        

        # Send the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_info,
                'message_id': saved_message['id'],
                'timestamp': saved_message['timestamp']
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        message_id = event['message_id']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'message_id': message_id,
            'timestamp': timestamp
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

    @database_sync_to_async
    def save_message_to_db(self, room_id, sender_id, message):
        try:
            print("Saving message to db")
            chat_room = ChatRoom.objects.get(id=room_id)
            sender = CustomUser.objects.get(id=sender_id)
            chat_message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=sender,
                content=message
            )
            print("Saved message to db", chat_message)
            return {
                'id': chat_message.id,
                'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        except ChatRoom.DoesNotExist:
            return {'id': None, 'timestamp': ''}
