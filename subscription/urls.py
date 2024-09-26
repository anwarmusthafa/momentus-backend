from django.urls import path
from .views import SubcriptionPlanAPIView , CreateCheckoutSession

urlpatterns = [
    path('subcriptionplan/', SubcriptionPlanAPIView.as_view(), name='comments-list'),
    path('subcriptionplan/<int:pk>/', SubcriptionPlanAPIView.as_view(), name='comments-list'),
    path('create-checkout-session/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    
]
