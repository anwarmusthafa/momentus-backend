from django.urls import path
from .views import ChatRoomView, GetChatroomsView
urlpatterns = [

    path('chat/<int:id>/', ChatRoomView.as_view(), name='chat_room'),
    path('chatrooms/', GetChatroomsView.as_view(), name='get_chatrooms'),

   
]
