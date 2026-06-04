import uuid
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.conversations.models import (
    Conversation,
    ConversationReadState,
    Fan,
    Message,
    ResponseTimer,
)
from apps.model_accounts.models import ModelAccount

DEMO_PASSWORD = "password123"

DEMO_USERS = [
    {
        "username": "lead",
        "email": "lead@example.com",
        "role": UserProfile.Role.TEAMLEAD,
        "display_name": "Team Lead",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "chatter1",
        "email": "chatter1@example.com",
        "role": UserProfile.Role.CHATTER,
        "display_name": "Chatter One",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "chatter2",
        "email": "chatter2@example.com",
        "role": UserProfile.Role.CHATTER,
        "display_name": "Chatter Two",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "chatter3",
        "email": "chatter3@example.com",
        "role": UserProfile.Role.CHATTER,
        "display_name": "Chatter Three",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "role": UserProfile.Role.ADMIN,
        "display_name": "Admin User",
        "is_staff": True,
        "is_superuser": True,
    },
]

DEMO_MODEL_ACCOUNTS = [
    "Model Aurora",
    "Model Luna",
    "Model Stella",
]

DEMO_FANS = [
    ("fan_001", "Fan Alex"),
    ("fan_002", "Fan Mike"),
    ("fan_003", "Fan Chris"),
    ("fan_004", "Fan Daniel"),
    ("fan_005", "Fan Nick"),
    ("fan_006", "Fan Sam"),
    ("fan_007", "Fan Leo"),
    ("fan_008", "Fan Max"),
]

DEMO_CONVERSATIONS = [
    {"fan": "fan_001", "chatter": "chatter1", "model": "Model Aurora", "waiting": False},
    {"fan": "fan_002", "chatter": "chatter1", "model": "Model Luna", "waiting": True, "overdue_seconds": 60},
    {"fan": "fan_003", "chatter": "chatter1", "model": "Model Stella", "waiting": True, "overdue_seconds": 120},
    {"fan": "fan_004", "chatter": "chatter2", "model": "Model Aurora", "waiting": False},
    {"fan": "fan_005", "chatter": "chatter2", "model": "Model Luna", "waiting": True, "overdue_seconds": 0},
    {"fan": "fan_006", "chatter": "chatter2", "model": "Model Stella", "waiting": False, "ppv": True},
    {"fan": "fan_007", "chatter": "chatter3", "model": "Model Aurora", "waiting": True, "overdue_seconds": 30},
    {"fan": "fan_008", "chatter": "chatter3", "model": "Model Luna", "waiting": False},
]


@dataclass
class SeedMessageSpec:
    sender_type: str
    text: str
    message_type: str = Message.MessageType.TEXT
    ppv_price: Decimal | None = None


def demo_message_uuid(fan_external_id: str, sequence: int) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_DNS, f"crm-demo-{fan_external_id}-msg-{sequence}")


def build_message_specs(waiting: bool, include_ppv: bool) -> list[SeedMessageSpec]:
    specs = [
        SeedMessageSpec(Message.SenderType.FAN, "Hey, are you online?"),
        SeedMessageSpec(Message.SenderType.CHATTER, "Hi! Yes, happy to chat."),
        SeedMessageSpec(Message.SenderType.FAN, "I wanted to ask about your latest content."),
        SeedMessageSpec(Message.SenderType.CHATTER, "Sure, what would you like to know?"),
    ]
    if include_ppv:
        specs.append(
            SeedMessageSpec(
                Message.SenderType.CHATTER,
                "I put together something special for you.",
                message_type=Message.MessageType.PPV,
                ppv_price=Decimal("19.99"),
            )
        )
        specs.extend(
            [
                SeedMessageSpec(Message.SenderType.FAN, "That sounds great, I'll check it out."),
                SeedMessageSpec(Message.SenderType.CHATTER, "Let me know what you think!"),
            ]
        )
    else:
        specs.extend(
            [
                SeedMessageSpec(Message.SenderType.FAN, "Do you have anything new this week?"),
                SeedMessageSpec(Message.SenderType.CHATTER, "Yes, I posted yesterday."),
            ]
        )

    if waiting:
        specs.append(
            SeedMessageSpec(
                Message.SenderType.FAN,
                "Hello? Still waiting for your reply.",
            )
        )
    else:
        specs.append(
            SeedMessageSpec(
                Message.SenderType.CHATTER,
                "Thanks for chatting today!",
            )
        )

    return specs


def build_message_timestamps(
    message_count: int,
    waiting: bool,
    overdue_seconds: int,
    now,
    sla_seconds: int,
) -> tuple[list, object | None]:
    if waiting:
        if overdue_seconds > 0:
            waiting_since = now - timedelta(seconds=sla_seconds + overdue_seconds)
        else:
            waiting_since = now - timedelta(minutes=5)

        timestamps = []
        for index in range(message_count):
            minutes_before = (message_count - 1 - index) * 5
            timestamps.append(waiting_since - timedelta(minutes=minutes_before))
        return timestamps, waiting_since

    anchor = now - timedelta(hours=2)
    timestamps = [anchor + timedelta(minutes=index * 5) for index in range(message_count)]
    return timestamps, None


class Command(BaseCommand):
    help = "Seed demo CRM data for local testing"

    def handle(self, *args, **options):
        with transaction.atomic():
            stats = self._seed_all()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("")
        self.stdout.write(f"Users: {stats['users']}")
        self.stdout.write(f"Model accounts: {stats['model_accounts']}")
        self.stdout.write(f"Fans: {stats['fans']}")
        self.stdout.write(f"Conversations: {stats['conversations']}")
        self.stdout.write(f"Messages: {stats['messages']}")
        self.stdout.write(f"Response timers: {stats['response_timers']}")
        self.stdout.write("")
        self.stdout.write("Accounts:")
        for username in ["lead", "chatter1", "chatter2", "chatter3", "admin"]:
            self.stdout.write(f"- {username} / {DEMO_PASSWORD}")

    def _seed_all(self) -> dict[str, int]:
        now = timezone.now()
        sla_seconds = settings.RESPONSE_SLA_SECONDS

        users = self._seed_users()
        model_accounts = self._seed_model_accounts()
        fans = self._seed_fans()

        for spec in DEMO_CONVERSATIONS:
            fan = fans[spec["fan"]]
            chatter = users[spec["chatter"]]
            model_account = model_accounts[spec["model"]]
            waiting = spec["waiting"]
            overdue_seconds = spec.get("overdue_seconds", 0)
            include_ppv = spec.get("ppv", False)

            conversation, _ = Conversation.objects.update_or_create(
                fan=fan,
                defaults={
                    "model_account": model_account,
                    "assigned_chatter": chatter,
                    "status": Conversation.Status.ACTIVE,
                },
            )

            message_specs = build_message_specs(waiting=waiting, include_ppv=include_ppv)
            timestamps, waiting_since = build_message_timestamps(
                len(message_specs),
                waiting,
                overdue_seconds,
                now,
                sla_seconds,
            )

            messages: list[Message] = []
            for index, (message_spec, created_at) in enumerate(
                zip(message_specs, timestamps, strict=True),
                start=1,
            ):
                sender_user = chatter if message_spec.sender_type == Message.SenderType.CHATTER else None

                message, _ = Message.objects.update_or_create(
                    conversation=conversation,
                    client_message_id=demo_message_uuid(spec["fan"], index),
                    defaults={
                        "sender_type": message_spec.sender_type,
                        "sender_user": sender_user,
                        "message_type": message_spec.message_type,
                        "text": message_spec.text,
                        "ppv_price": message_spec.ppv_price,
                    },
                )
                Message.objects.filter(pk=message.pk).update(created_at=created_at)
                message.refresh_from_db()
                messages.append(message)

            fan_messages = [m for m in messages if m.sender_type == Message.SenderType.FAN]
            chatter_messages = [m for m in messages if m.sender_type == Message.SenderType.CHATTER]
            last_message = messages[-1]
            last_fan_message = fan_messages[-1]
            last_chatter_message = chatter_messages[-1] if chatter_messages else None

            last_fan_message_at = last_fan_message.created_at
            last_chatter_message_at = (
                last_chatter_message.created_at if last_chatter_message else None
            )

            Conversation.objects.filter(pk=conversation.pk).update(
                last_message=last_message,
                last_message_at=last_message.created_at,
                waiting_since=waiting_since,
                last_fan_message_at=last_fan_message_at,
                last_chatter_message_at=last_chatter_message_at,
            )
            conversation.refresh_from_db()

            ResponseTimer.objects.filter(conversation=conversation).delete()

            if waiting:
                started_by_message = last_fan_message
                ResponseTimer.objects.create(
                    conversation=conversation,
                    status=ResponseTimer.Status.WAITING,
                    started_by_message=started_by_message,
                    started_at=started_by_message.created_at,
                )
            else:
                started_by_message = fan_messages[-2] if len(fan_messages) >= 2 else fan_messages[-1]
                stopped_by_message = last_chatter_message or last_message
                response_seconds = max(
                    0,
                    int(
                        (stopped_by_message.created_at - started_by_message.created_at).total_seconds()
                    ),
                )
                ResponseTimer.objects.create(
                    conversation=conversation,
                    status=ResponseTimer.Status.ANSWERED,
                    started_by_message=started_by_message,
                    stopped_by_message=stopped_by_message,
                    started_at=started_by_message.created_at,
                    stopped_at=stopped_by_message.created_at,
                    response_seconds=response_seconds,
                )

            if waiting:
                unread_count = max(1, len(fan_messages) - len(chatter_messages))
                last_read_message = last_chatter_message
                last_read_at = last_chatter_message.created_at if last_chatter_message else None
            else:
                unread_count = 0
                last_read_message = last_message
                last_read_at = last_message.created_at

            ConversationReadState.objects.update_or_create(
                conversation=conversation,
                user=chatter,
                defaults={
                    "last_read_message": last_read_message,
                    "last_read_at": last_read_at,
                    "unread_count": unread_count,
                },
            )

        fan_ids = list(fans.keys())
        return {
            "users": User.objects.filter(username__in=[u["username"] for u in DEMO_USERS]).count(),
            "model_accounts": ModelAccount.objects.filter(name__in=DEMO_MODEL_ACCOUNTS).count(),
            "fans": Fan.objects.filter(external_id__in=fan_ids).count(),
            "conversations": Conversation.objects.filter(fan__external_id__in=fan_ids).count(),
            "messages": Message.objects.filter(conversation__fan__external_id__in=fan_ids).count(),
            "response_timers": ResponseTimer.objects.filter(
                conversation__fan__external_id__in=fan_ids
            ).count(),
        }

    def _seed_users(self) -> dict[str, User]:
        users: dict[str, User] = {}
        for spec in DEMO_USERS:
            user, _ = User.objects.get_or_create(
                username=spec["username"],
                defaults={"email": spec["email"]},
            )
            user.email = spec["email"]
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            user.set_password(DEMO_PASSWORD)
            user.save()

            profile = user.profile
            profile.role = spec["role"]
            profile.display_name = spec["display_name"]
            profile.save()

            users[spec["username"]] = user
        return users

    def _seed_model_accounts(self) -> dict[str, ModelAccount]:
        accounts: dict[str, ModelAccount] = {}
        for name in DEMO_MODEL_ACCOUNTS:
            account, _ = ModelAccount.objects.get_or_create(name=name)
            accounts[name] = account
        return accounts

    def _seed_fans(self) -> dict[str, Fan]:
        fans: dict[str, Fan] = {}
        for external_id, display_name in DEMO_FANS:
            fan, _ = Fan.objects.get_or_create(
                external_id=external_id,
                defaults={"display_name": display_name},
            )
            if fan.display_name != display_name:
                fan.display_name = display_name
                fan.save(update_fields=["display_name"])
            fans[external_id] = fan
        return fans
