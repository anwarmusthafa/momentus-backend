import os
import django

# Set the default settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'momentus.settings')

# Initialize Django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from realtime.middleware import JWTAuthMiddleware
import realtime.routing

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP handling
    "websocket": JWTAuthMiddleware(  # Use custom JWT middleware
        URLRouter(
            realtime.routing.websocket_urlpatterns  # WebSocket routing
        )
    ),
})
