from django.urls import path
from .views import UsersAPI, BlockUser
urlpatterns = [
    path('users/', UsersAPI.as_view(), name='users'),
    path('users/<int:user_id>/block/', BlockUser.as_view(), name='block-user'),

]
