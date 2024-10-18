from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView , LogoutAPIView, health_check
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
    path("logout/", LogoutAPIView.as_view(), name='logout'),
    path("", include("posts.urls")),
    path("", include("realtime.urls")),
    path("momentus/admin/", include("admin_app.urls")),
    path("",include("subscription.urls")),
    path("health/", health_check, name='health-check'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)