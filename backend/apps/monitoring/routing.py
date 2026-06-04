from django.urls import path

from apps.monitoring.consumers import MonitorConsumer

websocket_urlpatterns = [
    path("ws/monitor/", MonitorConsumer.as_asgi()),
]
