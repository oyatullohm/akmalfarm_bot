from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import main.routing
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings')

application = ProtocolTypeRouter(
    {
        "http":get_asgi_application(),
        "websocket":AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(main.routing.websocket_urlpatterns))
        )
    }
)
