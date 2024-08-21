from django.urls import path
from .views import MyInbox
urlpatterns = [
    path('my-messages/', MyInbox.as_view(), name='chat-list'),
]
