from django.urls import path
from .views import PostAPI, MyPosts

urlpatterns = [
    path('post/', PostAPI.as_view(), name='post-create'),
    path('my-posts',MyPosts.as_view(),name='my_posts' ),
]
