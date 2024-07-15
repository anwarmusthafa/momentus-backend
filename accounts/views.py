from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny , IsAuthenticated
from django.contrib.auth import get_user_model
import random
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer, VerifyEmailSerializer
from .models import CustomUser
from .utils import send_verification_email
from rest_framework.views import APIView

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
            user.verification_code = verification_code
            print(verification_code)
            user.save()
            send_verification_email(user.username, verification_code)
            return Response({'message': 'User registered. Check your email for verification code.', 'user': user.id}, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            error_messages = e.detail
            response_errors = {}
            for field, messages in error_messages.items():
                response_errors[field] = messages[0] 

            return Response({'error': response_errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log any other exceptions
            print(f"Exception: {str(e)}")

            # Return a generic error message
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
            user_verification_code = str(user.verification_code).strip()
            print("otp",user.verification_code, verification_code)
            if user.verification_code != verification_code:
                print('Invalid verification code:', verification_code)
                return Response({'error': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
            if user.email_verified:
                print('Email already verified for user:', user_id)
                return Response({'message': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            if user.verification_code == verification_code:
                user.email_verified = True
                user.save()
                print('Email verified for user:', user_id)
            return Response({'message': 'Email verified successfully. Please login'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            print('User not found:', user_id)
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            print('Validation error:', e.detail)
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
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
            user = CustomUser.objects.filter(username=credentials['username']).first()
            if user is None:
                print('User not found:', credentials['username'])
                raise serializers.ValidationError('Invalid username or password.')
            
            if not user.email_verified:
                print('Email not verified for user:', user.id)
                raise serializers.ValidationError('Email is not verified.')

            # Call the parent class's validate method
            return super().validate(attrs)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            raise serializers.ValidationError('An error occurred during authentication. Please try again.')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ForgotPassword(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("forgotpassword")
            email = request.data.get('email')
            user = CustomUser.objects.get(username=email)
            if user:
                verification_code = str(random.randint(1000, 9999))
                user.verification_code = verification_code
                user.save()
                send_verification_email(user.username, verification_code)
                return Response({'message': 'Email sent. Check your email for verification code.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ForgotPasswordOTP(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            print("forgotpasswordotp")
            email = request.data.get('email')
            otp = request.data.get('otp')
            user = CustomUser.objects.get(username=email)
            if user:
                if user.verification_code == otp:
                    return Response({"message":"Otp is verified , Please reset the password"},status=status.HTTP_200_OK)
                else:
                    return Response({"error":"Otp is invalid, Try Again"},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error":"User not found"},status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ResetPassword(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            email = request.data.get('email')
            otp = request.data.get('otp')
            new_password = request.data.get('new_password')

            user = CustomUser.objects.get(username=email)
            if user and user.verification_code == otp:
                # Validate the new password
                serializer = UserSerializer()
                try:
                    validated_password = serializer.validate_password(new_password)
                except serializers.ValidationError as e:
                    return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(validated_password)
                user.save()
                return Response({"message": "Password reset is successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GetProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = CustomUser.objects.get(id=user.id)
            serializer = UserSerializer(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)





        

                
            

        
