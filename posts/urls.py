from django.urls import path
from .views import PostAPI

urlpatterns = [
    path('post/', PostAPI.as_view(), name='post-create'),
]
