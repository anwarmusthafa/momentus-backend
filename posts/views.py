from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment , Like
from .serializers import PostSerializer ,  CommentSerializer , LikeSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny 
from django.shortcuts import get_object_or_404
from django.db.models import Count
from itertools import chain
from rest_framework.exceptions import ValidationError

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
    def patch(self, request, id):
        try:
            post = get_object_or_404(Post, id=id)
            if post.user == request.user:
                caption = request.data.get('caption')
                if caption:
                    post.caption = caption
                post.save()
                serializer = PostSerializer(post)
                return Response("Post updated successfully", status=status.HTTP_200_OK)
            else:
                return Response({"error": "You do not have permission to update this post"}, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MyPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,momentus_user_name):
        try:
            momentus_user_name = momentus_user_name
            my_posts = Post.objects.filter(user__momentus_user_name=momentus_user_name , is_blocked=False).order_by('-created_at')
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
            # Fetch the post with the given ID and ensure it is not blocked
            post = Post.objects.filter(id=id, is_blocked=False).first()
            if not post:
                return Response({"error": "Post not found or is blocked"}, status=status.HTTP_404_NOT_FOUND)
            
            like_count = Like.objects.filter(post=post).count()
            comment_count = Comment.objects.filter(post=post).count()
            liked_by_user = Like.objects.filter(post=post, user=request.user).exists()
            
            serializer = PostSerializer(post, context={'request': request})
            post_data = dict(serializer.data)  # Make a copy of the data to make it mutable
            post_data['like_count'] = like_count
            post_data['comment_count'] = comment_count
            post_data['liked_by_user'] = liked_by_user
            
            return Response(post_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Comments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            post_id = id
            comments = Comment.objects.filter(post__id=post_id, parent__isnull=True)
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, id):
        try:
            post_id = id
            data = request.data
            data['post'] = post_id
            data['user'] = request.user.id
            parent_comment_id = data.get('parent', None)
            
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                data['parent'] = parent_comment.id
            
            serializer = CommentSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response("Comment created successfully", status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            if comment.user == request.user or comment.post.user == request.user:
                comment.delete()
                return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You do not have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
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

class ExploreView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            # Get popular posts (e.g., most liked) excluding blocked posts
            popular_posts = Post.objects.filter(is_blocked=False).annotate(like_count=Count('like')).order_by('-like_count')[:10]

            # Get latest posts excluding blocked posts
            latest_posts = Post.objects.filter(is_blocked=False).order_by('-created_at')[:10]

            # Combine the two querysets and remove duplicates
            combined_posts = list(chain(popular_posts, latest_posts))
            combined_posts = list({post.id: post for post in combined_posts}.values())[:20]  # Limit to 20 posts

            serializer = PostSerializer(combined_posts, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            print(f"Error in ExploreView: {str(e)}")
            return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


