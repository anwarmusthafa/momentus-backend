from django.urls import path
from .views import PersonalChatRoomView, GetChatroomsView , CreateGroupChatView , GroupChatView
urlpatterns = [

    path('chat/<int:id>/', PersonalChatRoomView.as_view(), name='chat_room'),
    path('chatrooms/', GetChatroomsView.as_view(), name='get_chatrooms'),
    path('create-group-chat/', CreateGroupChatView.as_view(), name='create_group_chat'),
    path('group-chat/<int:id>/', GroupChatView.as_view(), name='group_chat'),
   
]
