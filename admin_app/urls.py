from django.urls import path
from .views import UsersAPI, BlockUser , PostsAPI , BlockPost
urlpatterns = [
    path('users/', UsersAPI.as_view(), name='users'),
    path('user/<int:user_id>/block/', BlockUser.as_view(), name='block-user'),
    path('posts/', PostsAPI.as_view(), name='posts'),
    path('post/<int:post_id>/block/', BlockPost.as_view(), name='block-post'),

]
