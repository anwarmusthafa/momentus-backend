from rest_framework import serializers
from .models import ChatRoom, ChatParticipant, ChatMessage
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.files.storage import default_storage

class ChatParticipantSerializer(serializers.ModelSerializer): # Make sure UserSerializer is correctly defined
    profile_picture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id',  'momentus_user_name', 'profile_picture']
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'is_group', 'created_at', 'participants']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = ChatParticipantSerializer()

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_room', 'sender', 'content', 'image', 'timestamp', 'seen_by']
