from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from realtime.models import ChatRoom  # Lazy import
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Ensure the chat room exists and user is a participant
        room = await self.get_chat_room(self.room_id)
        if not room:
            await self.close()
            return

        participants = await self.get_room_participants(room)
        if self.user not in participants or not self.user.is_authenticated:
            await self.close()
            return

        # Add the user to the channel group and accept connection
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group on disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        from realtime.models import ChatMessage  # Lazy import
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender')

        # Fetch sender info and save message to the database
        sender_info = await self.get_user_info_by_id(sender_id)
        saved_message = await self.save_message_to_db(self.room_id, sender_id, message)

        if not saved_message.get('id'):
            print(f"Message not saved: {saved_message.get('error')}")
            return

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_info,
                'message_id': saved_message['id'],
                'timestamp': saved_message['timestamp'],
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_chat_room(self, room_id):
        from realtime.models import ChatRoom  # Lazy import
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_room_participants(self, room):
        return list(room.participants.all())

    @database_sync_to_async
    def get_user_info_by_id(self, user_id):
        from accounts.models import CustomUser  # Lazy import
        try:
            user = CustomUser.objects.get(id=user_id)
            return {
                'id': user.id,
                'username': user.momentus_user_name,
                'profile_picture': user.profile_picture.url if user.profile_picture else ''
            }
        except CustomUser.DoesNotExist:
            return {'username': 'Unknown', 'profile_picture': ''}

    @database_sync_to_async
    def save_message_to_db(self, room_id, sender_id, message):
        from realtime.models import ChatRoom, ChatMessage  # Lazy import
        from accounts.models import CustomUser  # Lazy import
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            sender = CustomUser.objects.get(id=sender_id)
            chat_message = ChatMessage.objects.create(
                chat_room=chat_room, sender=sender, content=message
            )
            return {
                'id': chat_message.id,
                'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        except (ChatRoom.DoesNotExist, CustomUser.DoesNotExist) as e:
            return {'error': str(e), 'id': None, 'timestamp': ''}
        except Exception as e:
            return {'error': 'An unexpected error occurred', 'id': None, 'timestamp': ''}
        


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"notifications_{self.scope['user'].id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_notification',
                
                'message': data['message'],
                'notification_type': data['notification_type']
            }
        )

    async def send_notification(self, event):
    # Extracting data from the event
        message = event.get('message')
        notification_type = event.get('notification_type')
        sender = event.get('sender')
        sender_image = event.get('sender_image')
        post_id = event.get('post_id')
        post_image = event.get('post_image')
        comment_id = event.get('comment_id')
        comment = event.get('comment')
    
        # Creating the response dictionary dynamically
        response_data = {}
    
        if message is not None:
            response_data['message'] = message
        if sender is not None:
            response_data['sender'] = sender
        if sender_image is not None:
            response_data['sender_image'] = sender_image
        if post_id is not None:
            response_data['post_id'] = post_id
        if post_image is not None:
            response_data['post_image'] = post_image
        if comment_id is not None:
            response_data['comment_id'] = comment_id
        if comment is not None:
            response_data['comment'] = comment
        if notification_type is not None:
            response_data['notification_type'] = notification_type
    
        # Send the response only if there's data to send
        if response_data:
            await self.send(text_data=json.dumps(response_data))

