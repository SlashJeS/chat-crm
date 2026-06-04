websocket_urlpatterns = []

try:
    from apps.realtime.routing import websocket_urlpatterns as realtime_patterns

    websocket_urlpatterns.extend(realtime_patterns)
except ImportError:
    pass

try:
    from apps.monitoring.routing import websocket_urlpatterns as monitoring_patterns

    websocket_urlpatterns.extend(monitoring_patterns)
except ImportError:
    pass
