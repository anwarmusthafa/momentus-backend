from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class MyInbox(APIView):
    
    def get(self, request):
        messages = ChatMessage.objects.filter(receiver=request.user).order_by('-created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
