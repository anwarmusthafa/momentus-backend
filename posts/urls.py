from django.urls import path
from .views import PostAPI, MyPosts, Comments, PostDetailView , LikePost , UnLikePost , ExploreView

urlpatterns = [
    path('comments/<int:post_id>/', Comments.as_view(), name='comments-list'),
    path('my-posts/<str:momentus_user_name>/',MyPosts.as_view(),name='my_posts' ),
    path('comments',Comments.as_view(),name='comments' ),
    path('post-details/<int:id>/', PostDetailView.as_view(), name='post_details'),
    path('create-post/', PostAPI.as_view(), name='create_post'),
    path('delete-post/<int:id>/', PostAPI.as_view(), name='delete_post'),
    path('like-post/<int:post_id>/', LikePost.as_view(), name='like_post'),
    path('unlike-post/<int:post_id>/', UnLikePost.as_view(), name='like_post'),
    path('explore/', ExploreView.as_view(), name='explore'),
]
