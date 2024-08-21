from django.urls import path
from .views import ChatRoomView
urlpatterns = [

    path('chat/<int:id>/', ChatRoomView.as_view(), name='chat_room'),
   
]
