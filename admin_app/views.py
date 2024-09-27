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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.core.cache import cache
from django.utils.timezone import now
from django.db.models import Count, Sum
from subscription.models import UserSubscription, Payment
from posts.models import Post, Like, Comment
from accounts.models import Friendship


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

class DashboardAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # Try to get cached data
        cache_key = "admin_dashboard_data"
        cached_data = cache.get(cache_key)
        


        if cached_data:
            print("cahecd data",cached_data)
            return Response(cached_data)  # Return cached data

        # Cache not found, regenerate the data
        total_users = CustomUser.objects.count()
        total_posts = Post.objects.count()
        total_active_subscriptions = UserSubscription.objects.filter(is_active=True).count()
        total_revenue = Payment.objects.filter(payment_status='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
        total_revenue_this_month = Payment.objects.filter(
            payment_date__month=now().month, payment_status='Completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        total_revenue_this_year = Payment.objects.filter(
        payment_date__year=now().year,
        payment_status='Completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_revenue_this_week = Payment.objects.filter(
        payment_date__week=now().isocalendar()[1],  # Get the week number from isocalendar
        payment_date__year=now().year,  # Ensure it's within the current year
        payment_status='Completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        top_liked_posts = Post.objects.annotate(likes_count=Count('likes')).order_by('-likes_count')[:3]
        top_liked_posts_data = [
            {'post_id': post.id, 'caption': post.caption, 'likes': post.likes_count}
            for post in top_liked_posts
        ]
        top_commented_posts = Post.objects.annotate(comments_count=Count('comments')).order_by('-comments_count')[:3]
        top_commented_posts_data = [
            {'post_id': post.id, 'caption': post.caption, 'comments': post.comments_count}
            for post in top_commented_posts
        ]
        total_comments = Comment.objects.count()
        total_likes = Like.objects.count()
        posts_today = Post.objects.filter(created_at__date=now().date()).count()
        total_users_with_subscription = UserSubscription.objects.filter(is_active=True).values('user').distinct().count()
        total_expired_subscriptions = UserSubscription.objects.filter(subscription_status='Expired').count()
        pending_friend_requests = Friendship.objects.filter(status='pending').count()
        top_users_with_posts = CustomUser.objects.annotate(post_count=Count('post')).order_by('-post_count')[:3]
        top_users_with_posts_data = [
            {'user_id': user.id, 'username': user.momentus_user_name, 'post_count': user.post_count}
            for user in top_users_with_posts
        ]
        total_new_users_this_month = CustomUser.objects.filter(date_joined__month=now().month).count()

        # Store the generated data
        data = {
            'total_users': total_users,
            'total_posts': total_posts,
            'total_active_subscriptions': total_active_subscriptions,
            'total_revenue': total_revenue,
            'total_revenue_this_month': total_revenue_this_month,
            'total_revenue_this_year': total_revenue_this_year,
            'total_revenue_this_week': total_revenue_this_week,
            'top_liked_posts': top_liked_posts_data,
            'top_commented_posts': top_commented_posts_data,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'posts_today': posts_today,
            'total_users_with_subscription': total_users_with_subscription,
            'total_expired_subscriptions': total_expired_subscriptions,
            'pending_friend_requests': pending_friend_requests,
            'top_users_with_posts': top_users_with_posts_data,
            'total_new_users_this_month': total_new_users_this_month,
        }

        # Cache the data (with a timeout of 15 minutes or as desired)
        cache.set(cache_key, data, timeout=86400)  # Cache for 1 day

        print("data",data)

        return Response(data)