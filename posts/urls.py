from django.urls import path
from .views import PostAPI, MyPosts, Comments, PostDetailView

urlpatterns = [
    path('post/', PostAPI.as_view(), name='post_create'),
    path('my-posts',MyPosts.as_view(),name='my_posts' ),
    path('comments',Comments.as_view(),name='comments' ),
    path('post-details/<int:id>/', PostDetailView.as_view(), name='post_details'),
]
