from django.conf import settings
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.accounts.permissions import IsTeamleadOrAdmin
from apps.conversations.pagination import parse_message_limit
from apps.conversations.selectors import (
    conversation_has_older_messages,
    get_conversation_for_user,
    get_conversations_for_user,
    get_messages_for_conversation,
)
from apps.conversations.serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    ConversationReadStateSerializer,
    MessageSerializer,
)
from apps.conversations.services import create_fan_message, mark_conversation_read


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = get_conversations_for_user(request.user)
        serializer = ConversationListSerializer(
            conversations,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversation = get_conversation_for_user(request.user, pk)
        serializer = ConversationDetailSerializer(conversation, context={"request": request})
        return Response(serializer.data)


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversation = get_conversation_for_user(request.user, pk)
        limit = parse_message_limit(request.query_params.get("limit"))
        before_id = request.query_params.get("before_id")
        after_id = request.query_params.get("after_id")

        try:
            before_id = int(before_id) if before_id is not None else None
            after_id = int(after_id) if after_id is not None else None
        except (TypeError, ValueError):
            return Response(
                {"detail": "before_id and after_id must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if before_id is not None and after_id is not None:
            return Response(
                {"detail": "Provide only one of before_id or after_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        messages = get_messages_for_conversation(
            conversation,
            before_id=before_id,
            after_id=after_id,
            limit=limit,
        )

        if after_id is not None:
            has_more = False
            next_before_id = None
        elif messages:
            oldest_id = messages[0].id
            has_more = conversation_has_older_messages(conversation, oldest_id)
            next_before_id = oldest_id if has_more else None
        else:
            has_more = False
            next_before_id = None

        return Response(
            {
                "results": MessageSerializer(messages, many=True).data,
                "has_more": has_more,
                "next_before_id": next_before_id,
            }
        )


class ConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        conversation = get_conversation_for_user(request.user, pk)
        last_read_message_id = request.data.get("last_read_message_id")
        read_state = mark_conversation_read(
            request.user,
            conversation,
            last_read_message_id=last_read_message_id,
        )
        serializer = ConversationReadStateSerializer(read_state)
        return Response(serializer.data)


class DevSimulateFanMessagePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if settings.DEBUG:
            return True
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False
        return profile.role in (UserProfile.Role.TEAMLEAD, UserProfile.Role.ADMIN)


class SimulateFanMessageView(APIView):
    permission_classes = [DevSimulateFanMessagePermission]

    def post(self, request):
        conversation_id = request.data.get("conversation_id")
        text = request.data.get("text")

        if not conversation_id or not text:
            return Response(
                {"detail": "conversation_id and text are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_conversation_for_user(request.user, conversation_id)
        message = create_fan_message(conversation, text)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
