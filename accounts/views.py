from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny , IsAuthenticated
from django.contrib.auth import get_user_model
import random
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer, VerifyEmailSerializer , AdminTokenObtainPairSerializer , FriendshipSerializer ,FriendsListSerializer, UserFriendsListSeriailizer 
from .models import CustomUser ,Friendship
from .utils import send_verification_email
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password , check_password
from django.contrib.auth import authenticate
from django.utils import timezone
from realtime.utils import send_notification
from realtime.models import Notification
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken


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
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
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

class FriendRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_id = request.data.get('receiver_id')

        # Check if sender is trying to send a request to themselves
        if sender.id == int(receiver_id):
            return Response({"error": "You can't send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = CustomUser.objects.get(id=receiver_id)

            # Check if receiver is blocked
            if receiver.is_blocked:
                return Response({"error": "You can't send a friend request to a blocked user"}, status=status.HTTP_400_BAD_REQUEST)

            # Try to create a new friendship request or get an existing one
            friendship, created = Friendship.objects.get_or_create(
                sender=sender, 
                receiver=receiver,
                defaults={'status': 'pending'}
            )

            if created:
                # Successfully created a new friend request
                notification = Notification.objects.create(
                    
                    content="sent you a friend request",
                    user=receiver,
                    sender=sender,
                    notification_type="friend_request"
                )
                send_notification(user_id=receiver.id, sender = sender.momentus_user_name,message="sent you a friend request", notification_type="friend_request", sender_image=sender.profile_picture) 

            if not created:
                # Check the status of an existing friendship request
                if friendship.status == "pending":
                    return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
                elif friendship.status == "accepted":
                    return Response({"error": "Friend request already accepted"}, status=status.HTTP_400_BAD_REQUEST)
                elif friendship.status == "declined":
                    return Response({"error": "Friend request already declined"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Successfully created a new friend request
            serializer = FriendshipSerializer(friendship)
            return Response({"message": "Friend request sent successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request,pk):
        user = request.user
        try:
            friendship = Friendship.objects.get(id=pk)
            if friendship.sender == user:
                friendship.delete()
                return Response({"message": "Friendship request deleted successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except Friendship.DoesNotExist:
            return Response({"error": "Friendship request not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class PendingFriendshipsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        pending_requests = Friendship.objects.filter(reciever=user, status='pending')
        serializer = FriendshipSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, pk):
        try:
            friendship = Friendship.objects.get(pk=pk)
        except Friendship.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if friendship.receiver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action')
        if action == 'accept':
            friendship.status = 'accepted'
            friendship.accepted_at = timezone.now()
            friendship.save()
            serializer = FriendshipSerializer(friendship)
            Notification.objects.create(
                content="accepted your friend request",
                user=friendship.sender,
                sender=friendship.receiver,
                notification_type="friend_request"
            )
            send_notification(
                user_id=friendship.sender.id,
                sender = friendship.receiver.momentus_user_name,
                message="accepted your friend request",
                notification_type="friend_request",
                sender_image=friendship.receiver.profile_picture.url if friendship.receiver.profile_picture else None
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif action == 'decline':
            friendship.delete()
            return Response({'detail': 'Friend request declined.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

class MyFriendsApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Fetch all friendships where the user is either the sender or receiver
            friends = Friendship.objects.filter(Q(sender=user) | Q(receiver=user), status="accepted")

            # Serialize the data
            serializer = FriendsListSerializer(friends, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            return Response({"error": "Friendships not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Generic error handling
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request, pk):
        user = request.user
        try:
            # Try to fetch the friendship by primary key (pk)
            friendship = Friendship.objects.get(pk=pk)

            # Check if the current user is either the sender or receiver
            if friendship.sender == user or friendship.receiver == user:
                friendship.delete()
                return Response("Unfriend successful", status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this friendship."}, status=status.HTTP_403_FORBIDDEN)

        except Friendship.DoesNotExist:
            return Response({"error": "Friendship not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFriendsList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,user_id):
        try:
            user = User.objects.get(pk=user_id)
            friends = Friendship.objects.filter(Q(sender = user)|Q(receiver=user),status="accepted")
            serializer =  UserFriendsListSeriailizer(friends, many=True,context={'user':user,  'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error":"User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Friendship.DoesNotExist:
            return Response({"error":"Friendships not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)