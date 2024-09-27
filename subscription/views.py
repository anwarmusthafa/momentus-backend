from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import SubscriptionPlan, UserSubscription, Payment
from .serializers import SubscriptionPlanSerializer , UserSubscriptionSerializer
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.utils import timezone



stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://localhost:3000'

# Create your views here.

class SubcriptionPlanAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        try:
            plans = SubscriptionPlan.objects.filter(is_block=False)
            serializer = SubscriptionPlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except UserSubscription.DoesNotExist:
            return Response({"error": "User subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        name = request.data.get('name')
        description = request.data.get('description')
        duration_in_days = request.data.get('duration_in_days')
        price = request.data.get('price')

        print(request)

        if not (name and duration_in_days and price):
            return Response({"error":"Name, duration and price are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            duration_in_days = int(duration_in_days)
            price = float(price)
        except ValueError:
            return Response({"error":"Invalid data for duration or price"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = SubscriptionPlan.objects.create(name=name,
                                                   description=description,
                                                   duration_in_days=duration_in_days,
                                                   price=price)
            return Response({"message": "Subscription plan created successfully."},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def patch(self, request, pk):
        plan = get_object_or_404(SubscriptionPlan, pk=pk)
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        plan = get_object_or_404(SubscriptionPlan,pk=pk)
        plan.delete()
        return Response({"message":"plan deleted successfully"},status=status.HTTP_204_NO_CONTENT)


class CreateCheckoutSession(APIView):
    def post(self, request):
        user = request.user
        try:
            # Fetch the subscription plan
            plan_id = request.data.get('plan-id')
            if not plan_id:
                return Response({"error": "Plan ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            plan = get_object_or_404(SubscriptionPlan, pk=int(plan_id))
            
            # Calculate the amount in the smallest currency unit (paise)
            amount = int(plan.price * 100)  # Convert to paise
            
            # Define the currency
            currency = 'inr'
            
            # Begin atomic transaction
            with transaction.atomic():
                # Create a new Stripe checkout session
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': plan.name,  # Use the plan name as the product name
                            },
                            'unit_amount': amount,  # Price in paise
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url='http://localhost:3000/?success=true',
                    cancel_url='http://localhost:3000/?canceled=true',
                )

                # Create UserSubscription record after session creation
                user_subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=plan.duration_in_days)
                )

                # Create a payment record
                Payment.objects.create(
                    user=user,
                    subscription=user_subscription,
                    amount=plan.price,  # Store the actual price, not the amount in cents
                    transaction_id=checkout_session.id  # Use the Stripe session ID as the transaction ID
                )

                # Update user's `is_prime` status
                user.is_prime = True
                user.save()

            # Return the session ID to the client
            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        try:
            if user.is_prime:
                # Fetch active subscription for prime users
                subscription = UserSubscription.objects.filter(user=user, is_active=True).first()
                if subscription:
                    serializer = UserSubscriptionSerializer(subscription)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"error": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # For non-prime users, fetch all available subscription plans
                plans = SubscriptionPlan.objects.filter(is_block=False)
                serializer = SubscriptionPlanSerializer(plans, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response({"error": "User subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # For non-prime users, fetch all available subscription plans
    def post(self,request):
        user = request.user
        try:
            subscription_id = request.data.get('subscription-id')
            if not subscription_id:
                return Response({"error":"Subscription ID is required"},status=status.HTTP_400_BAD_REQUEST)
            print(subscription_id)
            subscription = UserSubscription.objects.get(id=subscription_id)
            if subscription.user == user or user.is_superuser:
                subscription.is_active = False
                subscription.subscription_status = 'Cancelled'
                subscription.end_date = timezone.now()
                user.is_prime = False
                subscription.save()
                user.save()
                return Response({"message":"Subscription cancelled successfully"},status=status.HTTP_200_OK)
            else:
                return Response({"error":"Permission denied"},status=status.HTTP_403_FORBIDDEN)
        except UserSubscription.DoesNotExist:
            return Response({"error":"Subscription not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)





