import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import realtime.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # existing HTTP
        "websocket": AuthMiddlewareStack(
            URLRouter(realtime.routing.websocket_urlpatterns)
        ),
    }
)
