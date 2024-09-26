from django.urls import path
from .views import SubcriptionPlanAPIView

urlpatterns = [
    path('subcriptionplan/', SubcriptionPlanAPIView.as_view(), name='comments-list'),
    path('subcriptionplan/<int:pk>/', SubcriptionPlanAPIView.as_view(), name='comments-list'),
    
]
