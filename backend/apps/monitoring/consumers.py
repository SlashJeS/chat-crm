import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import UserProfile
from apps.monitoring.services import get_serialized_monitor_snapshot
from apps.realtime.events import ServerEvents


class MonitorConsumer(AsyncJsonWebsocketConsumer):
    allowed_roles = (UserProfile.Role.TEAMLEAD, UserProfile.Role.ADMIN)
    monitor_group = "teamlead_monitor"

    async def connect(self):
        self.user = self.scope["user"]
        self.refresh_task = None

        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close()
            return

        profile = await self._get_profile()
        if profile is None or profile.role not in self.allowed_roles:
            await self.close()
            return

        await self.channel_layer.group_add(self.monitor_group, self.channel_name)
        await self.accept()
        await self._send_snapshot()
        self.refresh_task = asyncio.create_task(self._periodic_refresh())

    async def disconnect(self, close_code):
        if self.refresh_task is not None:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass

        await self.channel_layer.group_discard(self.monitor_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        if event_type == "monitor.refresh":
            await self._send_snapshot()
            return

        await self.send_json(
            {
                "type": ServerEvents.ERROR,
                "code": "unknown_event",
                "message": "Unknown event type",
            }
        )

    async def ws_monitor_snapshot(self, event):
        await self.send_json(event["payload"])

    async def _periodic_refresh(self):
        try:
            while True:
                await asyncio.sleep(settings.MONITOR_REFRESH_SECONDS)
                await self._send_snapshot()
        except asyncio.CancelledError:
            raise

    async def _send_snapshot(self):
        snapshot = await database_sync_to_async(get_serialized_monitor_snapshot)()
        await self.send_json(
            {
                "type": ServerEvents.MONITOR_SNAPSHOT,
                "snapshot": snapshot,
            }
        )

    @database_sync_to_async
    def _get_profile(self):
        return getattr(self.user, "profile", None)
