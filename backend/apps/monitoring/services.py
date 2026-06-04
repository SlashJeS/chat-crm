from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.conversations.models import Conversation
from apps.monitoring.serializers import MonitorChatterSerializer
from apps.presence.services import get_online_user_ids


def build_monitor_snapshot(*, active_only=False):
    now = timezone.now()
    overdue_threshold = now - timedelta(seconds=settings.RESPONSE_SLA_SECONDS)
    chatters = []

    users_qs = User.objects.filter(profile__role=UserProfile.Role.CHATTER)
    if active_only:
        users_qs = users_qs.filter(is_active=True)
    users = list(users_qs.select_related("profile"))
    online_user_ids = get_online_user_ids([user.id for user in users])

    for user in users:
        conversations = Conversation.objects.filter(
            assigned_chatter=user,
            status=Conversation.Status.ACTIVE,
        )
        waiting_conversations = conversations.filter(waiting_since__isnull=False)
        overdue_count = waiting_conversations.filter(waiting_since__lte=overdue_threshold).count()

        chatters.append(
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.profile.display_name,
                "role": user.profile.role,
                "is_online": user.id in online_user_ids,
                "active_conversations_count": conversations.count(),
                "waiting_conversations_count": waiting_conversations.count(),
                "overdue_conversations_count": overdue_count,
                "last_seen_at": user.profile.last_seen_at,
            }
        )

    return {
        "sla_seconds": settings.RESPONSE_SLA_SECONDS,
        "presence_grace_seconds": settings.PRESENCE_GRACE_SECONDS,
        "chatters": chatters,
    }


def get_serialized_monitor_snapshot():
    snapshot = build_monitor_snapshot()
    snapshot["chatters"] = MonitorChatterSerializer(snapshot["chatters"], many=True).data
    return snapshot


def build_chatter_workload_list():
    snapshot = build_monitor_snapshot(active_only=True)
    return [
        {
            "id": chatter["id"],
            "username": chatter["username"],
            "display_name": chatter["display_name"],
            "is_online": chatter["is_online"],
            "active_conversations_count": chatter["active_conversations_count"],
            "waiting_conversations_count": chatter["waiting_conversations_count"],
            "overdue_conversations_count": chatter["overdue_conversations_count"],
            "last_seen_at": chatter["last_seen_at"],
        }
        for chatter in snapshot["chatters"]
    ]
