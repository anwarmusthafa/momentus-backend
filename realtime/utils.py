from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification(user_id, message,notification_type,post_image=None,momentus_user_name = None,sender_image=None,post_id=None,comment_id=None):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            'type': 'send_notification',
            'message': message,
            'sender': momentus_user_name if momentus_user_name else None,
            "sender_image": sender_image if sender_image else None,
            'post_id': post_id if post_id else None,
            'comment_id': comment_id if comment_id else None,
            'post_image': post_image if post_image else None,

            'notification_type': notification_type,
        }
    )
