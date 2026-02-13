from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # room_id values in this app look like "1-2" so we must allow '-'
    re_path(r"ws/chat/(?P<room_id>[\w-]+)/$", ChatConsumer.as_asgi()),
]