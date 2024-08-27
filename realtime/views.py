from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatParticipant, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class ChatPagination(PageNumberPagination):
    page_size = 10  # Set to 10 results per page
    page_size_query_param = 'page_size'  # Allow clients to override this using ?page_size=

class ChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print("kwargs", kwargs)
        user_to_chat_id = kwargs.get('id')
        user_to_chat = get_object_or_404(User, id=user_to_chat_id)
        current_user = request.user

        # Check if the chat room already exists
        chat_room = ChatRoom.objects.filter(
            is_group=False,
            participants=current_user
        ).filter(participants=user_to_chat).first()
        print(chat_room)

        if not chat_room:
            print("chat room not found")
            # Create a new chat room
            chat_room = ChatRoom.objects.create(is_group=False)
             # Prepare ChatParticipant instances for bulk creation
            participants = [
                ChatParticipant(user=current_user, chat_room=chat_room),
                ChatParticipant(user=user_to_chat, chat_room=chat_room)
            ]
        
        # get this chat room last 10 messages using pagination
        chat_messages = ChatMessage.objects.filter(chat_room=chat_room).order_by('-timestamp')
        print(chat_messages)

        # Initialize pagination
        paginator = ChatPagination()
        paginated_chat_messages = paginator.paginate_queryset(chat_messages, request)
        
        # Serialize paginated data
        serializer = ChatMessageSerializer(paginated_chat_messages, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
        

        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChatRoomPagination(PageNumberPagination):
    page_size = 10  # Set to 10 results per page
    page_size_query_param = 'page_size'  # Allow clients to override this using ?page_size=

class GetChatroomsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ChatRoomPagination

    def get(self, request, *args, **kwargs):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(participants=user)
        
        # Initialize pagination
        paginator = self.pagination_class()
        paginated_chat_rooms = paginator.paginate_queryset(chat_rooms, request)
        
        # Serialize paginated data
        serializer = ChatRoomSerializer(paginated_chat_rooms, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)


