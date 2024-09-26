from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import SubscriptionPlan, UserSubscription, Payment
from .serializers import SubscriptionPlanSerializer
from django.shortcuts import get_object_or_404

# Create your views here.

class SubcriptionPlanAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            plans = SubscriptionPlan.objects.all()
            serializer = SubscriptionPlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            serializer.save()  # Save the changes if data is valid
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        plan = get_object_or_404(SubscriptionPlan,pk=pk)
        plan.delete()
        return Response({"message":"plan deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        

