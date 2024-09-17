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

        # Check if room exists and if user is a participant
        room = await self.get_chat_room(self.room_id)

        if room is None:
            # Room doesn't exist, close the connection
            await self.close()
            return

        self.room = room
        participants = await self.get_room_participants(self.room)

        if self.user not in participants:
            print("User is not part of the chat room")
            # User is not part of the chat room, close the connection
            await self.close()
            return

        # If user is authenticated and part of the room, allow WebSocket connection
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
        message = text_data_json.get('message')
        sender_id = text_data_json.get('sender')
        chat_room_id = self.room_id

        print(f"Received message: {message} {sender_id} {chat_room_id}")

        # Get sender info and save the message to the database
        sender_info = await self.get_user_info_by_id(sender_id)
        saved_message = await self.save_message_to_db(chat_room_id, sender_id, message)
        
        # Check if the message was successfully saved
        if not saved_message.get('id'):
            print(f"Message not saved, error: {saved_message.get('error')}")
            return  # Don't send the message to the WebSocket if saving failed

        print("Sending message to room group", sender_id, self.user.id)
        
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
    def get_chat_room(self, room_id):
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_room_participants(self, room):
        return list(room.participants.all())

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
        print("Saving message to db, room: ", room_id, sender_id, message)
        try:
            # Fetch chat room and sender, handle exceptions separately
            chat_room = ChatRoom.objects.get(id=room_id)
            sender = CustomUser.objects.get(id=sender_id)

            # Create the message after confirming room and sender exist
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

        except (ChatRoom.DoesNotExist, CustomUser.DoesNotExist) as e:
            print(f"An error occurred: {str(e)}")
            return {'id': None, 'timestamp': '', 'error': str(e)}

        except Exception as e:
            print(f"An error occurred while saving message: {str(e)}")
            return {'id': None, 'timestamp': '', 'error': 'An error occurred'}
        


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

