from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    momentus_user_name = models.CharField(max_length=20, unique=True)
    is_prime = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_code = models.TextField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)


    # Ensure related_name is unique to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser'
    )
    def __str__(self):
        return f"{self.username}+{self.id}"
# accounts/models.py

class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="friendship_initated")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="friendship_recieved")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.momentus_user_name} + {self.receiver.momentus_user_name} + {self.id}"
    


    
