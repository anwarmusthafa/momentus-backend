from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment , Like
from .serializers import PostSerializer ,  CommentSerializer , LikeSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny 
from django.shortcuts import get_object_or_404

class PostAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id):
        post = get_object_or_404(Post, id=id)
        if post.user == request.user:
            post.delete()
            return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You do not have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)

class MyPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,momentus_user_name):
        try:
            momentus_user_name = momentus_user_name
            my_posts = Post.objects.filter(user__momentus_user_name=momentus_user_name).order_by('-created_at')
            serializer = PostSerializer(my_posts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Posts not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            post = Post.objects.get(id=id)
            like_count = Like.objects.filter(post=post).count()
            comment_count = Comment.objects.filter(post=post).count()
            liked_by_user = Like.objects.filter(post=post, user=request.user).exists()
            serializer = PostSerializer(post, context={'request': request})
            post_data = dict(serializer.data)  # Make a copy of the data to make it mutable
            post_data['like_count'] = like_count
            post_data['comment_count'] = comment_count
            post_data['liked_by_user'] = liked_by_user
            return Response(post_data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class Comments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            comments = Comment.objects.filter(post__id=post_id)
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            data = request.data
            data['post'] = post.id
            data['user'] = request.user.id

            serializer = CommentSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            data = request.data
            data['post'] = post.id
            data['user'] = request.user.id
            serializer = LikeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UnLikePost(APIView):
    def post(self, request, post_id):
        try:
            like = Like.objects.get(post=post_id, user=request.user)
            like.delete()
            return Response({"message": "Like deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


