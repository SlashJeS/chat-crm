from django.urls import path

from apps.monitoring.views import MonitorSnapshotView

urlpatterns = [
    path("snapshot/", MonitorSnapshotView.as_view(), name="monitor-snapshot"),
]
