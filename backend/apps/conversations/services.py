from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserProfile
from apps.conversations.models import Conversation, ConversationReadState, Message, ResponseTimer
from apps.realtime.publishers import (
    publish_conversation_updated_for_user,
    publish_conversation_updated,
    publish_message_created,
    publish_monitor_snapshot,
    publish_read_state_updated,
)


def _schedule_fan_message_events(message_id, conversation_id):
    def publish():
        publish_message_created(message_id)
        publish_conversation_updated(conversation_id)
        publish_monitor_snapshot()

    transaction.on_commit(publish)


def _schedule_mark_read_events(read_state_id, conversation_id, user_id):
    def publish():
        publish_read_state_updated(read_state_id)
        publish_conversation_updated(conversation_id, user_id=user_id)
        publish_monitor_snapshot()

    transaction.on_commit(publish)


def _schedule_chatter_message_events(message_id, conversation_id, user_id, read_state_id=None):
    def publish():
        publish_message_created(message_id)
        publish_conversation_updated(conversation_id, user_id=user_id)
        if read_state_id is not None:
            publish_read_state_updated(read_state_id)
        publish_monitor_snapshot()

    transaction.on_commit(publish)


def mark_conversation_read(user, conversation, last_read_message_id=None):
    read_state, _ = ConversationReadState.objects.get_or_create(
        conversation=conversation,
        user=user,
    )

    if last_read_message_id is not None:
        try:
            last_read_message = Message.objects.get(
                pk=last_read_message_id,
                conversation=conversation,
            )
        except Message.DoesNotExist as exc:
            raise ValidationError({"last_read_message_id": "Message not found in conversation."}) from exc
    else:
        last_read_message = conversation.last_message

    read_state.last_read_message = last_read_message
    read_state.last_read_at = timezone.now()
    read_state.unread_count = 0
    read_state.save()

    _schedule_mark_read_events(read_state.id, conversation.id, user.id)
    return read_state


@transaction.atomic
def create_fan_message(conversation, text):
    waiting_since_was_null = conversation.waiting_since is None

    message = Message.objects.create(
        conversation=conversation,
        sender_type=Message.SenderType.FAN,
        message_type=Message.MessageType.TEXT,
        text=text,
    )

    conversation.last_message = message
    conversation.last_message_at = message.created_at
    conversation.last_fan_message_at = message.created_at
    if waiting_since_was_null:
        conversation.waiting_since = message.created_at
    conversation.save(
        update_fields=[
            "last_message",
            "last_message_at",
            "last_fan_message_at",
            "waiting_since",
            "updated_at",
        ]
    )

    read_state, _ = ConversationReadState.objects.get_or_create(
        conversation=conversation,
        user=conversation.assigned_chatter,
    )
    read_state.unread_count += 1
    read_state.save(update_fields=["unread_count", "updated_at"])

    if waiting_since_was_null:
        ResponseTimer.objects.create(
            conversation=conversation,
            started_by_message=message,
            started_at=message.created_at,
            status=ResponseTimer.Status.WAITING,
        )

    _schedule_fan_message_events(message.id, conversation.id)
    return message


@transaction.atomic
def create_chatter_message(
    user,
    conversation,
    text,
    message_type=Message.MessageType.TEXT,
    ppv_price=None,
    client_message_id=None,
):
    if conversation.assigned_chatter_id != user.id:
        raise PermissionDenied("You are not the assigned chatter for this conversation.")

    if client_message_id is not None:
        existing = Message.objects.filter(
            conversation=conversation,
            client_message_id=client_message_id,
        ).first()
        if existing is not None:
            return existing, False

    if message_type == Message.MessageType.PPV:
        if ppv_price is None or ppv_price <= Decimal("0"):
            raise ValidationError({"ppv_price": "PPV messages must have a price greater than 0."})
    elif message_type == Message.MessageType.TEXT:
        if ppv_price is not None:
            raise ValidationError({"ppv_price": "Text messages must not have a PPV price."})
    else:
        raise ValidationError({"message_type": "Unsupported message type."})

    message = Message(
        conversation=conversation,
        sender_type=Message.SenderType.CHATTER,
        sender_user=user,
        message_type=message_type,
        text=text,
        ppv_price=ppv_price if message_type == Message.MessageType.PPV else None,
        client_message_id=client_message_id,
    )
    message.save()

    conversation.last_message = message
    conversation.last_message_at = message.created_at
    conversation.last_chatter_message_at = message.created_at
    conversation.waiting_since = None
    conversation.save(
        update_fields=[
            "last_message",
            "last_message_at",
            "last_chatter_message_at",
            "waiting_since",
            "updated_at",
        ]
    )

    timer = (
        ResponseTimer.objects.filter(
            conversation=conversation,
            status=ResponseTimer.Status.WAITING,
        )
        .order_by("-started_at")
        .first()
    )
    if timer is not None:
        timer.stopped_by_message = message
        timer.stopped_at = message.created_at
        timer.response_seconds = max(
            0,
            int((timer.stopped_at - timer.started_at).total_seconds()),
        )
        timer.status = ResponseTimer.Status.ANSWERED
        timer.save()

    read_state, _ = ConversationReadState.objects.get_or_create(
        conversation=conversation,
        user=user,
    )
    read_state.last_read_message = message
    read_state.last_read_at = timezone.now()
    read_state.unread_count = 0
    read_state.save()

    _schedule_chatter_message_events(message.id, conversation.id, user.id, read_state.id)
    return message, True


def _schedule_assignment_events(conversation_id, old_chatter_id, new_chatter_id):
    def publish():
        if old_chatter_id is not None:
            publish_conversation_updated_for_user(conversation_id, old_chatter_id)
        publish_conversation_updated_for_user(conversation_id, new_chatter_id)
        publish_monitor_snapshot()

    transaction.on_commit(publish)


@transaction.atomic
def assign_conversation_to_chatter(*, conversation, chatter, assigned_by):
    if chatter.profile.role != UserProfile.Role.CHATTER:
        raise ValidationError({"chatter_id": "Target user must have the CHATTER role."})
    if not chatter.is_active:
        raise ValidationError({"chatter_id": "Target user must be active."})

    if conversation.status != Conversation.Status.ACTIVE:
        raise ValidationError({"detail": "Only ACTIVE conversations can be assigned."})

    conversation = Conversation.objects.select_for_update().get(pk=conversation.pk)

    if conversation.assigned_chatter_id == chatter.id:
        return conversation

    old_chatter_id = conversation.assigned_chatter_id
    conversation.assigned_chatter = chatter
    conversation.save(update_fields=["assigned_chatter", "updated_at"])

    unread_count = 1 if conversation.waiting_since is not None else 0
    ConversationReadState.objects.get_or_create(
        conversation=conversation,
        user=chatter,
        defaults={"unread_count": unread_count},
    )

    _schedule_assignment_events(conversation.id, old_chatter_id, chatter.id)
    return conversation
