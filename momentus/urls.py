from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("posts.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
