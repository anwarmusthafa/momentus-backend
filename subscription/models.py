from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Choice for payment statuses
PAYMENT_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Failed', 'Failed'),
]

# Choice for subscription status
SUBSCRIPTION_STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Expired', 'Expired'),
    ('Cancelled', 'Cancelled'),
]

class SubscriptionPlan(models.Model):
    name = models.CharField(
        max_length=50,
    )  # 'Monthly', 'Yearly', etc.
    description = models.TextField(blank=True, null=True)
    duration_in_days = models.IntegerField()  # 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class UserSubscription(models.Model):  # Fixed typo (Modal -> Model)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    payment_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending'
    )
    subscription_status = models.CharField(
        max_length=50, choices=SUBSCRIPTION_STATUS_CHOICES, default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'

    # Method to check if the subscription is still valid
    @property
    def is_valid(self):
        return self.is_active and self.end_date >= timezone.now().date()


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(default='Stripe')
    payment_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending'
    )
    transaction_id = models.CharField(max_length=100, unique=True)  # Payment gateway transaction ID

    def __str__(self):
        return f'Payment {self.transaction_id} - {self.payment_status}'
