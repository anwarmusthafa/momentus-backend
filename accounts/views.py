from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny , IsAuthenticated
from django.contrib.auth import get_user_model
import random
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer, VerifyEmailSerializer , AdminTokenObtainPairSerializer , FollowSerializer
from .models import CustomUser , Follow
from .utils import send_verification_email
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password , check_password
from django.contrib.auth import authenticate

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            print(request.data)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            verification_code = str(random.randint(1000, 9999))
            
            # Hash the verification code
            hashed_code = make_password(verification_code)
            user.verification_code = hashed_code
            print(verification_code)
            user.save()
            send_verification_email(user.username, verification_code)
            return Response({'message': 'User registered. Check your email for verification code.', 'user': user.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Error:', e)
            return Response({'error': 'An error occurred during registration. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        try:
            print('Received data:', request.data)
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print('Validation errors:', serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            print('Serializer validated data:', serializer.validated_data)
            verification_code = serializer.validated_data['verification_code']
            user_id = int(serializer.validated_data['user_id'])
            
            user = CustomUser.objects.get(id=user_id)
            
            # Verify the OTP
            if not check_password(verification_code, user.verification_code):
                print('Invalid verification code:', verification_code)
                return Response({'error': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.email_verified:
                print('Email already verified for user:', user_id)
                return Response({'message': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.email_verified = True
            user.save()
            print('Email verified for user:', user_id)
            return Response({'message': 'Email verified successfully. Please login'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            print('User not found:', user_id)
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('Exception:', e)
            return Response({'error': 'An error occurred during email verification. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            credentials = {
                'username': attrs.get('username'),
                'password': attrs.get('password')
            }
            user = authenticate(
                request=None,  # You can pass a request object here if needed
                username=credentials['username'],
                password=credentials['password']
            )

            if user is None:
                print('User not found:', credentials['username'])
                raise serializers.ValidationError('Invalid username or password.')
            
            if not user.email_verified:
                print('Email not verified for user:', user.id)
                raise serializers.ValidationError('Email is not verified.')

            if user.is_blocked:
                print('User is blocked by Admin:', user.id)
                raise serializers.ValidationError('User is blocked by Admin.')

            # Call the parent class's validate method
            return super().validate(attrs)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            raise serializers.ValidationError('An error occurred during authentication. Please try again.')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AdminTokenObtainPairView(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer


class ForgotPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            user = CustomUser.objects.filter(username=email).first()
            if user:
                verification_code = str(random.randint(1000, 9999))
                
                # Hash the verification code
                hashed_code = make_password(verification_code)
                user.verification_code = hashed_code
                user.save()
                
                send_verification_email(user.username, verification_code)
                return Response({'message': 'Email sent. Check your email for verification code.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ForgotPasswordOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            otp = request.data.get('otp')
            user = CustomUser.objects.filter(username=email).first()
            if user:
                # Verify the OTP
                if check_password(otp, user.verification_code):
                    return Response({"message": "OTP is verified. Please reset the password"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "OTP is invalid. Try again"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            otp = request.data.get('otp')
            new_password = request.data.get('new_password')

            # Ensure all required fields are provided
            if not all([email, otp, new_password]):
                return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the user by email
            user = CustomUser.objects.get(username=email)

            # Validate OTP using check_password
            if check_password(otp, user.verification_code):
                # Validate the new password
                serializer = UserSerializer()
                try:
                    validated_password = serializer.validate_password(new_password)
                except serializers.ValidationError as e:
                    return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

                # Set the new password and save the user
                user.set_password(validated_password)
                user.save()

                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        try:
            profile = CustomUser.objects.get(id=user.id)
            serializer = UserSerializer(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        user = request.user
        profile = get_object_or_404(CustomUser, id=user.id)
        serializer = UserSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            updated_profile = CustomUser.objects.get(id=user.id)
            updated_serializer = UserSerializer(updated_profile, context={'request': request})
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfile(APIView):
    permission_classes = [AllowAny]
    def get(self, request, momentus_user_name):
        try:
            user = CustomUser.objects.get(momentus_user_name=momentus_user_name)
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class SearchUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return Response({"error": "Invalid query"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            users = CustomUser.objects.filter(momentus_user_name__icontains=query)[:5]
            serializer = UserSerializer(users, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
User = get_user_model()

class FollowAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed_user')
        user = request.user

        if not followed_user_id:
            return Response({'error': 'followed_user is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if already followed
        if Follow.objects.filter(user=user, followed_user=followed_user).exists():
            return Response({'error': 'Already following this user'}, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow(user=user, followed_user=followed_user)
        follow.save()
        serializer = FollowSerializer(follow)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed_user')
        user = request.user

        if not followed_user_id:
            return Response({'error': 'followed_user is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            follow = Follow.objects.get(user=user, followed_user=followed_user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)
class FollowingList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        following = Follow.objects.filter(user=user)
        serializer = FollowSerializer(following, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowersList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        followers = Follow.objects.filter(followed_user=user)
        serializer = FollowSerializer(followers, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    