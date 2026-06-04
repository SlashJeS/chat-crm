from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.db.models import Prefetch

from apps.conversations.models import Conversation, ConversationReadState, Message
from apps.conversations.serializers import (
    ConversationListSerializer,
    ConversationReadStateSerializer,
    MessageSerializer,
)
from apps.realtime.events import ChannelEvents, ServerEvents


def get_dialog_group_name(conversation_id):
    return f"dialog_{conversation_id}"


def get_chatter_group_name(user_id):
    return f"chatter_{user_id}"


def get_teamlead_monitor_group_name():
    return "teamlead_monitor"


def _get_channel_layer():
    return get_channel_layer()


def _serialize_message(message):
    return MessageSerializer(message).data


def _serialize_conversation(conversation, user=None):
    if user is not None:
        read_states = getattr(conversation, "current_user_read_states", None)
        if read_states is None:
            conversation = (
                Conversation.objects.filter(pk=conversation.pk)
                .select_related(
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
                .first()
            )
    return ConversationListSerializer(conversation, context={"user": user}).data


def _serialize_read_state(read_state):
    return ConversationReadStateSerializer(read_state).data


def publish_message_created(message_id):
    message = (
        Message.objects.select_related(
            "conversation",
            "sender_user",
            "sender_user__profile",
        )
        .filter(pk=message_id)
        .first()
    )
    if message is None:
        return

    channel_layer = _get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": ServerEvents.MESSAGE_CREATED,
        "message": _serialize_message(message),
    }
    async_to_sync(channel_layer.group_send)(
        get_dialog_group_name(message.conversation_id),
        {
            "type": ChannelEvents.MESSAGE_CREATED,
            "payload": payload,
        },
    )


def publish_conversation_updated(conversation_id, user_id=None):
    target_user_id = user_id
    conversation = (
        Conversation.objects.select_related(
            "fan",
            "model_account",
            "assigned_chatter",
            "assigned_chatter__profile",
            "last_message",
            "last_message__sender_user",
            "last_message__sender_user__profile",
        )
        .filter(pk=conversation_id)
        .first()
    )
    if conversation is None:
        return

    channel_layer = _get_channel_layer()
    if channel_layer is None:
        return

    if target_user_id is None:
        target_user_id = conversation.assigned_chatter_id

    if target_user_id is None:
        return

    publish_conversation_updated_for_user(conversation_id, target_user_id)


def publish_conversation_updated_for_user(conversation_id, user_id):
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        return

    conversation = (
        Conversation.objects.filter(pk=conversation_id)
        .select_related(
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
        .first()
    )
    if conversation is None:
        return

    channel_layer = _get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": ServerEvents.CONVERSATION_UPDATED,
        "conversation": _serialize_conversation(conversation, user=user),
    }
    async_to_sync(channel_layer.group_send)(
        get_chatter_group_name(user_id),
        {
            "type": ChannelEvents.CONVERSATION_UPDATED,
            "payload": payload,
        },
    )


def publish_read_state_updated(read_state_id):
    read_state = (
        ConversationReadState.objects.select_related(
            "conversation",
            "user",
            "last_read_message",
            "last_read_message__sender_user",
            "last_read_message__sender_user__profile",
        )
        .filter(pk=read_state_id)
        .first()
    )
    if read_state is None:
        return

    channel_layer = _get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": ServerEvents.READ_STATE_UPDATED,
        "conversation_id": read_state.conversation_id,
        "read_state": _serialize_read_state(read_state),
    }
    event = {
        "type": ChannelEvents.READ_STATE_UPDATED,
        "payload": payload,
    }
    async_to_sync(channel_layer.group_send)(
        get_chatter_group_name(read_state.user_id),
        event,
    )
    async_to_sync(channel_layer.group_send)(
        get_dialog_group_name(read_state.conversation_id),
        event,
    )


def publish_monitor_snapshot():
    from apps.monitoring.services import get_serialized_monitor_snapshot

    channel_layer = _get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": ServerEvents.MONITOR_SNAPSHOT,
        "snapshot": get_serialized_monitor_snapshot(),
    }
    async_to_sync(channel_layer.group_send)(
        get_teamlead_monitor_group_name(),
        {
            "type": ChannelEvents.MONITOR_SNAPSHOT,
            "payload": payload,
        },
    )
