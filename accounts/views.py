import string
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
import random

User = get_user_model()

from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer
from .models import CustomUser

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .utils import send_verification_email  # Ensure `generate_otp` is defined if used
from rest_framework.permissions import AllowAny
import random
import string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers


User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
    
        
        # Generate a verification code
        verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        user.verification_code = verification_code
        user.save()

        # Send verification email
        send_verification_email(user.email, verification_code)

        return Response({'message': 'User registered. Check your email for verification code.'}, status=status.HTTP_201_CREATED)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        verification_code = request.data.get('verification_code')
        
        if not verification_code:
            return Response({'error': 'Verification code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find the user based on the verification code
            user = CustomUser.objects.get(verification_code=verification_code)
            if user.email_verified:
                return Response({'message': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the user as verified
            user.email_verified = True
            user.verification_code = None
            user.save()
            
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def validate(cls, attrs):
        data = super().validate(attrs)
        user = cls.get_user(attrs['username'])
        
        # Check if the user's email is verified
        if not user.email_verified:
            raise serializers.ValidationError('Email is not verified.')
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
