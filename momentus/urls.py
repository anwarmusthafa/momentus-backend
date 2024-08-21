from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import AdminTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('admin-login/', AdminTokenObtainPairView.as_view(), name='admin_login'),
    path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("posts.urls")),
    path("", include("chat.urls")),
    path("", include("admin_app.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)