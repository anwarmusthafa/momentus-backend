from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def invalidate_user_profile_cache(sender, instance, **kwargs):
    # Invalidate the cache when the user profile is updated
    cache_key = f"profile:{instance.id}"
    cache.delete(cache_key)
