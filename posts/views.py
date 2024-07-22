from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer ,  CommentSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny

class PostAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [ AllowAny]

    def get(self, request,id):
        try:
            post = Post.objects.get(id=id)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class Comments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            post_id = request.query_params.get('post-id')  # Use query parameters for GET requests
            if not post_id:
                return Response({"error": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            comments = Comment.objects.filter(post__id=post_id)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


