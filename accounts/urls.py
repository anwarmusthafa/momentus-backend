from django.urls import path
from .views import RegisterUserView, VerifyEmailView, ForgotPassword, ForgotPasswordOTP, ResetPassword , MyProfile , UserProfile, SearchUser , FriendRequestAPIView , PendingFriendshipsAPIView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPassword.as_view(), name='forgot_password'),
    path('forgot-password-otp/', ForgotPasswordOTP.as_view(), name='forgot_password_otp'),
    path('reset-password/', ResetPassword.as_view(), name='forgot_password_otp'),
    path('my-profile/', MyProfile.as_view(), name='get_my_profile'),
    path('user-profile/<str:momentus_user_name>/', UserProfile.as_view(), name='user_profile'),
    path('search-user/', SearchUser.as_view(), name='search_user'),
    path('friendrequest/', FriendRequestAPIView.as_view(), name='friendship-create'),
    path('friendrequest/<int:pk>/', FriendRequestAPIView.as_view(), name='friendship-create'),
    path('pending-friendrequests/', PendingFriendshipsAPIView.as_view(), name='pending-friendships'),
    path('pending-friendrequests/<int:pk>/', PendingFriendshipsAPIView.as_view(), name='pending-friendships'),
    
]
