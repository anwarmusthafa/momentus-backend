from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from subscription.models import UserSubscription

@shared_task
def send_subscription_email(user_email, subscription_details):
    try:
        print("Sending subscription email to:", user_email)
        print("Subscription details:", subscription_details)
        
        subject = 'Your Subscription Details and Invoice'
        message = f"Dear Subscriber,\n\nThank you for subscribing to {subscription_details['plan_name']}.\n\n" \
                  f"Here are your subscription details:\n" \
                  f"Plan: {subscription_details['plan_name']}\n" \
                  f"Price: {subscription_details['amount']} INR\n" \
                  f"Start Date: {subscription_details['start_date']}\n" \
                  f"End Date: {subscription_details['end_date']}\n\n" \
                  f"Thank you for choosing us!"
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


@shared_task
def expire_subscriptions():
    today = timezone.now().date()
    expired_subscriptions = UserSubscription.objects.filter(end_date__lt=today, is_active=True)
    
    for subscription in expired_subscriptions:
        subscription.is_active = False
        subscription.subscription_status = 'Expired'
        subscription.save()

        # Update the user status
        user = subscription.user
        user.is_prime = False
        user.save()
