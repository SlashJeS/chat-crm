from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsTeamleadOrAdmin
from apps.monitoring.services import get_serialized_monitor_snapshot


class MonitorSnapshotView(APIView):
    permission_classes = [IsTeamleadOrAdmin]

    def get(self, request):
        return Response(get_serialized_monitor_snapshot())
