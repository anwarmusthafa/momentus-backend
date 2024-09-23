from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment , Like
from accounts.models import Friendship
from .serializers import PostSerializer ,  CommentSerializer , LikeSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny 
from django.shortcuts import get_object_or_404
from django.db.models import Count
from itertools import chain
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from realtime.utils import send_notification
from realtime.models import Notification
from django.db.models import Q

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
                print("caption",caption)
                if caption is not None:
                    post.caption = caption
                    post.save()
                    serializer = PostSerializer(post)
                    return Response("Post updated successfully", status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Caption cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
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
            post = Post.objects.get(id=post_id)
            
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                data['parent'] = parent_comment.id
            
            serializer = CommentSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                content = f"{request.user.momentus_user_name} commented on your post. {serializer.data['comment']}"
                notification = Notification.objects.create( content=content,
                                                            user=post.user,
                                                            sender=request.user,
                                                            post=post,
                                                            notification_type="comment")
                send_notification(user_id=post.user.id, sender = request.user.momentus_user_name, post_id=post.id, comment_id=serializer.data['id'], post_image=post.image.url, notification_type="comment")
                return Response("Comment created successfully", status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def patch(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            if comment.user == request.user:
                data = request.data
                serializer = CommentSerializer(comment, data=data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Comment updated successfully"}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "You do not have permission to edit this comment"}, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
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
                notification = Notification.objects.create(
                user=post.user,
                sender = request.user,
                post = post,
                notification_type='like'
                )
                send_notification(
                    post.user.id, 
                    notification.content, 
                    notification.notification_type, 
                    post.image.url,  # Pass image URL instead of the object
                    request.user.momentus_user_name,
                    post.user.profile_picture.url if post.user.profile_picture else None,  # Handle profile picture URL
                    post_id,
                )
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

class ExplorePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ExploreView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ExplorePagination
    def get(self, request):
        try:
            # Fetch posts, ordering by like count (popularity) and then by creation date (recency)
            posts = Post.objects.filter(is_blocked=False).annotate(
                like_count=Count('like')
            ).order_by('-like_count', '-created_at')

            # Paginate posts at the database level to fetch only 20 posts at a time
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            print(f"Error in ExploreView: {str(e)}")
            return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HomeFeedAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the current logged-in user
            user = request.user

            # Fetch friend IDs where the current user is either the sender or receiver, and the status is 'accepted'
            friends = Friendship.objects.filter(
                Q(sender=user) | Q(receiver=user),
                status='accepted'
            ).values_list('sender_id', 'receiver_id')

            # Extract friend IDs using set comprehension (exclude the current user's ID)
            friend_ids = {friend_id for friend_pair in friends for friend_id in friend_pair if friend_id != user.id}

            # Fetch the latest 20 posts from these friends, including related user data
            posts = Post.objects.filter(user_id__in=friend_ids).select_related('user').order_by('-created_at')[:20]

            # Check if there are no posts
            if not posts:
                return Response({"detail": "No posts available."}, status=204)

            # Serialize the posts
            serializer = PostSerializer(posts, many=True, context={"request": request})

            # Return the serialized posts in the response
            return Response(serializer.data, status=200)

        except Friendship.DoesNotExist:
            return Response({"error": "Friendship data not found."}, status=404)
        
        except Post.DoesNotExist:
            return Response({"error": "No posts found."}, status=404)
        
        except Exception as e:
            # Catch any other exceptions and log it if needed
            return Response({"error": str(e)}, status=500)


    


