from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(email, verification_code):
    subject = 'Verify Your Email'
    message = f'Your verification code is: {verification_code}'
    print(verification_code)
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
