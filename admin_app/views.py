from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.serializers import UserSerializer
from accounts.models import CustomUser
from rest_framework.views import APIView
from posts.models import Post
from posts.serializers import PostSerializer

class UsersAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            users = CustomUser.objects.exclude(is_superuser=True)
            serializer = UserSerializer(users, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class BlockUser(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.is_blocked = not user.is_blocked
        user.save()
        
        # Pass the request object to the serializer context
        serializer = UserSerializer(user, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlockPost(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        post.is_blocked = not post.is_blocked
        post.save()
        
        # Pass the request object to the serializer context
        serializer = PostSerializer(post, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)