from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatParticipant, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_to_chat_id = kwargs.get('id')
        user_to_chat = get_object_or_404(User, id=user_to_chat_id)
        current_user = request.user

        # Check if the chat room already exists
        chat_room = ChatRoom.objects.filter(
            is_group=False,
            participants=current_user
        ).filter(participants=user_to_chat).first()

        if not chat_room:
            # Create a new chat room
            chat_room = ChatRoom.objects.create(is_group=False)
            ChatParticipant.objects.create(user=current_user, chat_room=chat_room)
            ChatParticipant.objects.create(user=user_to_chat, chat_room=chat_room)

        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_200_OK)


