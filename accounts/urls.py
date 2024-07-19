from django.urls import path
from .views import RegisterUserView, VerifyEmailView, ForgotPassword, ForgotPasswordOTP, ResetPassword , Profile

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPassword.as_view(), name='forgot_password'),
    path('forgot-password-otp/', ForgotPasswordOTP.as_view(), name='forgot_password_otp'),
    path('reset-password/', ResetPassword.as_view(), name='forgot_password_otp'),
    path('profile/', Profile.as_view(), name='get_profile'),

]
