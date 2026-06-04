import uuid
from decimal import Decimal, InvalidOperation

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserProfile
from apps.conversations.models import Conversation, Message
from apps.conversations.selectors import get_conversation_for_user
from apps.conversations.services import create_chatter_message, mark_conversation_read
from apps.presence.services import heartbeat
from apps.realtime.events import ClientEvents, ServerEvents
from apps.realtime.publishers import (
    get_chatter_group_name,
    get_dialog_group_name,
    publish_monitor_snapshot,
)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    allowed_roles = (
        UserProfile.Role.CHATTER,
        UserProfile.Role.TEAMLEAD,
        UserProfile.Role.ADMIN,
    )

    async def connect(self):
        self.user = self.scope["user"]
        self.subscribed_dialog_ids: set[int] = set()

        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close()
            return

        profile = await self._get_profile()
        if profile is None or profile.role not in self.allowed_roles:
            await self.close()
            return

        self.chatter_group = get_chatter_group_name(self.user.id)
        await self.channel_layer.group_add(self.chatter_group, self.channel_name)
        await self.accept()
        await self.send_json({"type": ServerEvents.CONNECTION_ACCEPTED})

        if profile.role == UserProfile.Role.CHATTER:
            await self._heartbeat_and_publish_monitor()

    async def disconnect(self, close_code):
        if hasattr(self, "chatter_group"):
            await self.channel_layer.group_discard(self.chatter_group, self.channel_name)

        for conversation_id in getattr(self, "subscribed_dialog_ids", set()):
            await self.channel_layer.group_discard(
                get_dialog_group_name(conversation_id),
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        if event_type == ClientEvents.DIALOG_SUBSCRIBE:
            await self.handle_dialog_subscribe(content)
        elif event_type == ClientEvents.DIALOG_UNSUBSCRIBE:
            await self.handle_dialog_unsubscribe(content)
        elif event_type == ClientEvents.MESSAGE_SEND:
            await self.handle_message_send(content)
        elif event_type == ClientEvents.DIALOG_MARK_READ:
            await self.handle_dialog_mark_read(content)
        elif event_type == ClientEvents.PRESENCE_HEARTBEAT:
            await self.handle_presence_heartbeat()
        else:
            await self.send_error("unknown_event", "Unknown event type")

    async def handle_dialog_subscribe(self, content):
        conversation_id = content.get("conversation_id")
        if conversation_id is None:
            await self.send_error("invalid_payload", "conversation_id is required")
            return

        try:
            conversation_id = int(conversation_id)
        except (TypeError, ValueError):
            await self.send_error("invalid_payload", "conversation_id must be an integer")
            return

        conversation = await self._get_conversation(conversation_id)
        if conversation is None:
            await self.send_error("not_found", "Conversation not found")
            return

        group_name = get_dialog_group_name(conversation_id)
        await self.channel_layer.group_add(group_name, self.channel_name)
        self.subscribed_dialog_ids.add(conversation_id)
        await self.send_json(
            {
                "type": ServerEvents.DIALOG_SUBSCRIBED,
                "conversation_id": conversation_id,
            }
        )

    async def handle_dialog_unsubscribe(self, content):
        conversation_id = content.get("conversation_id")
        if conversation_id is None:
            await self.send_error("invalid_payload", "conversation_id is required")
            return

        try:
            conversation_id = int(conversation_id)
        except (TypeError, ValueError):
            await self.send_error("invalid_payload", "conversation_id must be an integer")
            return

        if conversation_id in self.subscribed_dialog_ids:
            await self.channel_layer.group_discard(
                get_dialog_group_name(conversation_id),
                self.channel_name,
            )
            self.subscribed_dialog_ids.discard(conversation_id)

        await self.send_json(
            {
                "type": ServerEvents.DIALOG_UNSUBSCRIBED,
                "conversation_id": conversation_id,
            }
        )

    async def handle_message_send(self, content):
        profile = await self._get_profile()
        if profile is None or profile.role != UserProfile.Role.CHATTER:
            await self.send_error("forbidden", "Only chatters can send messages")
            return

        conversation_id = content.get("conversation_id")
        text = content.get("text")
        message_type = content.get("message_type", Message.MessageType.TEXT)
        ppv_price = content.get("ppv_price")
        client_message_id = content.get("client_message_id")

        if conversation_id is None or not text:
            await self.send_error("invalid_payload", "conversation_id and text are required")
            return

        try:
            conversation_id = int(conversation_id)
        except (TypeError, ValueError):
            await self.send_error("invalid_payload", "conversation_id must be an integer")
            return

        conversation = await self._get_conversation(conversation_id)
        if conversation is None:
            await self.send_error("not_found", "Conversation not found")
            return

        parsed_client_message_id = None
        if client_message_id:
            try:
                parsed_client_message_id = uuid.UUID(str(client_message_id))
            except (TypeError, ValueError, AttributeError):
                await self.send_error("invalid_payload", "client_message_id must be a UUID")
                return

        parsed_ppv_price = None
        if ppv_price is not None:
            try:
                parsed_ppv_price = Decimal(str(ppv_price))
            except (InvalidOperation, TypeError, ValueError):
                await self.send_error("invalid_payload", "ppv_price must be a decimal")
                return

        try:
            message, _ = await database_sync_to_async(create_chatter_message)(
                self.user,
                conversation,
                text,
                message_type=message_type,
                ppv_price=parsed_ppv_price,
                client_message_id=parsed_client_message_id,
            )
        except PermissionDenied:
            await self.send_error("forbidden", "You are not the assigned chatter for this conversation")
            return
        except ValidationError as exc:
            await self.send_error("validation_error", str(exc.detail))
            return

        await self.send_json(
            {
                "type": ServerEvents.MESSAGE_SEND_ACK,
                "client_message_id": str(message.client_message_id) if message.client_message_id else None,
                "message_id": message.id,
            }
        )

    async def handle_dialog_mark_read(self, content):
        conversation_id = content.get("conversation_id")
        last_read_message_id = content.get("last_read_message_id")

        if conversation_id is None:
            await self.send_error("invalid_payload", "conversation_id is required")
            return

        try:
            conversation_id = int(conversation_id)
        except (TypeError, ValueError):
            await self.send_error("invalid_payload", "conversation_id must be an integer")
            return

        if last_read_message_id is not None:
            try:
                last_read_message_id = int(last_read_message_id)
            except (TypeError, ValueError):
                await self.send_error("invalid_payload", "last_read_message_id must be an integer")
                return

        conversation = await self._get_conversation(conversation_id)
        if conversation is None:
            await self.send_error("not_found", "Conversation not found")
            return

        try:
            await database_sync_to_async(mark_conversation_read)(
                self.user,
                conversation,
                last_read_message_id=last_read_message_id,
            )
        except ValidationError as exc:
            await self.send_error("validation_error", str(exc.detail))
            return

        await self.send_json(
            {
                "type": ServerEvents.DIALOG_MARK_READ_ACK,
                "conversation_id": conversation_id,
            }
        )

    async def handle_presence_heartbeat(self):
        profile = await self._get_profile()
        if profile is None or profile.role != UserProfile.Role.CHATTER:
            await self.send_error("forbidden", "Only chatters can send presence heartbeat")
            return

        last_seen_at = await self._heartbeat_and_publish_monitor()
        await self.send_json(
            {
                "type": ServerEvents.PRESENCE_HEARTBEAT_ACK,
                "last_seen_at": last_seen_at.isoformat() if last_seen_at else None,
            }
        )

    async def ws_message_created(self, event):
        await self.send_json(event["payload"])

    async def ws_conversation_updated(self, event):
        await self.send_json(event["payload"])

    async def ws_read_state_updated(self, event):
        await self.send_json(event["payload"])

    async def send_error(self, code, message):
        await self.send_json(
            {
                "type": ServerEvents.ERROR,
                "code": code,
                "message": message,
            }
        )

    @database_sync_to_async
    def _get_profile(self):
        return getattr(self.user, "profile", None)

    @database_sync_to_async
    def _get_conversation(self, conversation_id):
        try:
            return get_conversation_for_user(self.user, conversation_id)
        except Http404:
            return None

    @database_sync_to_async
    def _heartbeat_and_publish_monitor(self):
        last_seen_at = heartbeat(self.user)
        publish_monitor_snapshot()
        return last_seen_at
