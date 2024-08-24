from rest_framework import serializers
from .models import ChatRoom, ChatParticipant, ChatMessage
from accounts.serializers import UserSerializer

class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Make sure UserSerializer is correctly defined

    class Meta:
        model = ChatParticipant
        fields = ['user', 'chat_room', 'joined_at']

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
