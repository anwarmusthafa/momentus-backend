from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatRoom(models.Model):
    """
    Model to represent a chat room. This can be either personal (1-on-1) or group chat.
    """
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional for group chats
    is_group = models.BooleanField(default=False)  # To distinguish between 1-on-1 and group chat
    created_at = models.DateTimeField(auto_now_add=True)  # When the chat was created
    participants = models.ManyToManyField(User, through='ChatParticipant', related_name='chat_rooms')

    def __str__(self):
        if self.is_group and self.name:
            return f"Group: {self.name}"
        return f"Chat between {', '.join([user.username for user in self.participants.all()])}"

class ChatParticipant(models.Model):
    """
    Model to represent participants in a chat room.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    # is_admin = models.BooleanField(default=False)  # In case of group chat, some users can be admins

    def __str__(self):
        return f"{self.user.username} in {self.chat_room}"

class ChatMessage(models.Model):
    """
    Model to represent messages sent within a chat room.
    """
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Message content (text)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)  # Optional image
    timestamp = models.DateTimeField(default=timezone.now)  # Time when the message was sent
    seen_by = models.ManyToManyField(User, related_name='seen_messages', blank=True)  # Who has seen the message

    def __str__(self):
        return f"Message by {self.sender.username} in {self.chat_room}"

    class Meta:
        ordering = ['timestamp']  # Ensure messages are retrieved in chronological order
