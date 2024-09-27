from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan  
        fields="__all__"
class UserSubscriptionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ['id','plan','name','end_date',"is_active", "price",]

    def get_name(self, obj):
        return obj.plan.name

    def get_price(self, obj):
        return obj.plan.price
