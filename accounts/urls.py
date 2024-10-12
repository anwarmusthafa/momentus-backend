from django.urls import path
from .views import RegisterUserView, VerifyEmailView, ForgotPassword, ForgotPasswordOTP, ResetPassword , MyProfile , UserProfile, SearchUser , FriendRequestAPIView , PendingFriendshipsAPIView, MyFriendsApi, UserFriendsList, MutualFriendsList, health_check

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
    path('my-friends-list/', MyFriendsApi.as_view(), name="my-friends-list"),
    path("unfriend/<int:pk>/", MyFriendsApi.as_view(), name="unfriend"),
    path("other-friends-list/<int:user_id>/", UserFriendsList.as_view(), name="others-friends-list"),
    path("mutual-friends-list/<int:user_id>/", MutualFriendsList.as_view(), name="mutual-friends-list"),


    
]
