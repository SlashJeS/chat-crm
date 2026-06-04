from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsTeamleadOrAdmin
from apps.conversations.models import Conversation
from apps.conversations.selectors import (
    filter_lead_conversations_queryset,
    get_lead_conversation,
    get_lead_conversations_queryset,
)
from apps.conversations.serializers import (
    AssignConversationSerializer,
    LeadConversationSerializer,
)
from apps.conversations.services import assign_conversation_to_chatter
from apps.monitoring.services import build_chatter_workload_list


def _parse_limit_offset(query_params):
    try:
        limit = int(query_params.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 100))

    try:
        offset = int(query_params.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0
    offset = max(0, offset)

    return limit, offset


def _parse_optional_int(value, field_name):
    if value is None:
        return None, None
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, Response(
            {"detail": f"{field_name} must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LeadConversationListView(APIView):
    permission_classes = [IsTeamleadOrAdmin]

    def get(self, request):
        status_filter = request.query_params.get("status")
        if status_filter is not None and status_filter not in Conversation.Status.values:
            return Response(
                {"detail": "status must be ACTIVE or CLOSED."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assigned_chatter_id, error = _parse_optional_int(
            request.query_params.get("assigned_chatter_id"),
            "assigned_chatter_id",
        )
        if error is not None:
            return error

        model_account_id, error = _parse_optional_int(
            request.query_params.get("model_account_id"),
            "model_account_id",
        )
        if error is not None:
            return error

        queryset = filter_lead_conversations_queryset(
            get_lead_conversations_queryset(),
            status=status_filter,
            assigned_chatter_id=assigned_chatter_id,
            model_account_id=model_account_id,
            search=request.query_params.get("search") or None,
        )

        limit, offset = _parse_limit_offset(request.query_params)
        count = queryset.count()
        conversations = queryset[offset : offset + limit]
        serializer = LeadConversationSerializer(conversations, many=True)
        return Response({"count": count, "results": serializer.data})


class LeadConversationDetailView(APIView):
    permission_classes = [IsTeamleadOrAdmin]

    def get(self, request, pk):
        conversation = get_lead_conversation(pk)
        serializer = LeadConversationSerializer(conversation)
        return Response(serializer.data)


class LeadConversationAssignView(APIView):
    permission_classes = [IsTeamleadOrAdmin]

    def post(self, request, pk):
        conversation = get_lead_conversation(pk)
        serializer = AssignConversationSerializer(
            data=request.data,
            context={"conversation": conversation},
        )
        serializer.is_valid(raise_exception=True)

        updated = assign_conversation_to_chatter(
            conversation=conversation,
            chatter=serializer.context["chatter"],
            assigned_by=request.user,
        )
        updated = get_lead_conversation(updated.pk)
        return Response(LeadConversationSerializer(updated).data)


class LeadChatterWorkloadView(APIView):
    permission_classes = [IsTeamleadOrAdmin]

    def get(self, request):
        return Response({"results": build_chatter_workload_list()})
