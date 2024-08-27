from rest_framework import serializers
from .models import ChatRoom, ChatParticipant, ChatMessage
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatParticipantSerializer(serializers.ModelSerializer): # Make sure UserSerializer is correctly defined
    class Meta:
        model = User
        fields = ['id',  'momentus_user_name', 'profile_picture']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'is_group', 'created_at', 'participants']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_room', 'sender', 'content', 'image', 'timestamp', 'seen_by']
