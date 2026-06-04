from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.conversations.models import Conversation, Message
from apps.conversations.services import create_fan_message

logger = logging.getLogger(__name__)

DEMO_FAN_MESSAGES = [
    "Hey, are you online?",
    "What are you doing right now?",
    "I was waiting for your reply.",
    "Do you have anything new for me?",
    "Are you still here?",
    "Can you send me something special?",
    "I want to chat for a bit.",
    "Tell me more about that.",
    "I just came back to check your messages.",
    "That sounds interesting.",
]


@dataclass(frozen=True)
class DemoActivityConfig:
    min_interval_seconds: int = 18
    max_interval_seconds: int = 45
    batch_min: int = 1
    batch_max: int = 2
    only_assigned: bool = True
    min_seconds_between_messages_per_conversation: int = 45
    startup_delay_seconds: int = 8


def get_demo_activity_config() -> DemoActivityConfig:
    return DemoActivityConfig()


def _is_preferred_conversation(conversation: Conversation) -> bool:
    if conversation.waiting_since is None:
        return True
    if (
        conversation.last_message is not None
        and conversation.last_message.sender_type == Message.SenderType.CHATTER
    ):
        return True
    return False


def get_candidate_conversations(config: DemoActivityConfig) -> list[Conversation]:
    queryset = Conversation.objects.filter(status=Conversation.Status.ACTIVE).select_related(
        "fan",
        "model_account",
        "assigned_chatter",
        "assigned_chatter__profile",
        "last_message",
    )

    if config.only_assigned:
        queryset = queryset.filter(
            assigned_chatter__isnull=False,
            assigned_chatter__is_active=True,
            assigned_chatter__profile__role=UserProfile.Role.CHATTER,
        )

    cooldown = timedelta(seconds=config.min_seconds_between_messages_per_conversation)
    now = timezone.now()
    candidates: list[Conversation] = []

    for conversation in queryset:
        if (
            conversation.last_fan_message_at is not None
            and now - conversation.last_fan_message_at < cooldown
        ):
            continue
        candidates.append(conversation)

    candidates.sort(
        key=lambda conversation: (
            0 if _is_preferred_conversation(conversation) else 1,
            conversation.last_fan_message_at or timezone.datetime.min.replace(tzinfo=timezone.utc),
        )
    )
    return candidates


def select_conversations_for_batch(config: DemoActivityConfig) -> list[Conversation]:
    candidates = get_candidate_conversations(config)
    if not candidates:
        return []

    preferred = [conversation for conversation in candidates if _is_preferred_conversation(conversation)]
    pool = preferred if preferred else candidates
    batch_size = random.randint(config.batch_min, min(config.batch_max, len(pool)))
    return random.sample(pool, batch_size)


def generate_fan_message_text(conversation: Conversation) -> str:
    template = random.choice(DEMO_FAN_MESSAGES)

    fan_name = conversation.fan.display_name.strip()
    model_name = conversation.model_account.name.strip()

    if random.random() < 0.25 and fan_name:
        return f"Hi, it's {fan_name}. {template}"
    if random.random() < 0.25 and model_name:
        return f"Hey {model_name}, {template[0].lower()}{template[1:]}"
    return template


def run_demo_activity_once() -> dict:
    config = get_demo_activity_config()
    conversations = select_conversations_for_batch(config)

    if not conversations:
        return {
            "generated_count": 0,
            "conversation_ids": [],
            "skipped_reason": "no_candidates",
        }

    conversation_ids: list[int] = []
    for conversation in conversations:
        text = generate_fan_message_text(conversation)
        create_fan_message(conversation, text)
        conversation_ids.append(conversation.id)
        logger.info(
            "Generated demo fan message for conversation %s: %s",
            conversation.id,
            text,
        )

    return {
        "generated_count": len(conversation_ids),
        "conversation_ids": conversation_ids,
        "skipped_reason": None,
    }
