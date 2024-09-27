from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from posts.models import Post
from subscription.models import UserSubscription, Payment
from accounts.models import CustomUser
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Post)
@receiver([post_save, post_delete], sender=UserSubscription)
@receiver([post_save, post_delete], sender=Payment)
@receiver([post_save, post_delete], sender=CustomUser)
def clear_cache(sender, instance, **kwargs):
    cache.delete("admin_dashboard_data")  # Invalidate cache on any change
