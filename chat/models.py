from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )
    
    # Removed default="0" and if necessary, allow null values or provide a valid default.
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages', null=True)

    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
    
    @property
    def sender_profile(self):
        return self.sender

    @property
    def receiver_profile(self):
        return self.receiver




