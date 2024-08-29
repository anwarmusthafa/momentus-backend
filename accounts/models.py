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

class Friends(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'friend'],
                name='unique_friendship'
            ),
            models.UniqueConstraint(
                fields=['friend', 'user'],
                name='unique_reverse_friendship'
            )
        ]
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"


    
