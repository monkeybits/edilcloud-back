# chat/routing.py
from django.conf.urls import url, include

from . import consumers

websocket_urlpatterns = [
    url(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    url(r'ws/notify/(?P<room_name>\w+)/$', consumers.NotifyConsumer),
    url(r'ws/report/(?P<room_name>\w+)/$', consumers.ReportConsumer),
]