from datetime import timedelta

from django.conf import settings
from django.db.models import Prefetch
from django.http import Http404
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.conversations.models import Conversation, ConversationReadState, Message


def get_conversations_for_user(user):
    queryset = Conversation.objects.filter(status=Conversation.Status.ACTIVE)

    if user.profile.role == UserProfile.Role.CHATTER:
        queryset = queryset.filter(assigned_chatter=user)

    return (
        queryset.select_related(
            "fan",
            "model_account",
            "assigned_chatter",
            "assigned_chatter__profile",
            "last_message",
            "last_message__sender_user",
            "last_message__sender_user__profile",
        )
        .prefetch_related(
            Prefetch(
                "read_states",
                queryset=ConversationReadState.objects.filter(user=user),
                to_attr="current_user_read_states",
            )
        )
        .order_by("-last_message_at", "-updated_at")
    )


def get_conversation_for_user(user, conversation_id):
    try:
        return get_conversations_for_user(user).get(pk=conversation_id)
    except Conversation.DoesNotExist as exc:
        raise Http404 from exc


def get_messages_for_conversation(conversation, before_id=None, after_id=None, limit=30):
    limit = max(1, min(limit, 100))
    queryset = Message.objects.filter(conversation=conversation).select_related(
        "sender_user",
        "sender_user__profile",
    )

    if before_id is not None:
        messages = list(queryset.filter(id__lt=before_id).order_by("-id")[:limit])
        messages.reverse()
        return messages

    if after_id is not None:
        return list(queryset.filter(id__gt=after_id).order_by("id")[:limit])

    messages = list(queryset.order_by("-id")[:limit])
    messages.reverse()
    return messages


def conversation_has_older_messages(conversation, oldest_message_id):
    return Message.objects.filter(conversation=conversation, id__lt=oldest_message_id).exists()


def is_conversation_overdue(conversation, now=None):
    if not conversation.waiting_since:
        return False
    now = now or timezone.now()
    return conversation.waiting_since < now - timedelta(seconds=settings.RESPONSE_SLA_SECONDS)
