from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live/(?P<session_id>\d+)/$', consumers.LiveStreamConsumer.as_asgi()),
]