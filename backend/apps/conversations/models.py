from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Fan(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]
        indexes = [
            models.Index(fields=["external_id"]),
            models.Index(fields=["display_name"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class Conversation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    model_account = models.ForeignKey(
        "model_accounts.ModelAccount",
        related_name="conversations",
        on_delete=models.PROTECT,
    )
    fan = models.ForeignKey(
        Fan,
        related_name="conversations",
        on_delete=models.PROTECT,
    )
    assigned_chatter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_conversations",
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    last_message = models.ForeignKey(
        "Message",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    last_message_at = models.DateTimeField(null=True, blank=True)
    waiting_since = models.DateTimeField(null=True, blank=True)
    last_fan_message_at = models.DateTimeField(null=True, blank=True)
    last_chatter_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_message_at", "-updated_at"]
        indexes = [
            models.Index(fields=["assigned_chatter", "status"]),
            models.Index(fields=["status", "waiting_since"]),
            models.Index(fields=["model_account", "status"]),
            models.Index(fields=["fan"]),
            models.Index(fields=["last_message_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.fan} @ {self.model_account}"


class Message(models.Model):
    class SenderType(models.TextChoices):
        FAN = "FAN", "Fan"
        CHATTER = "CHATTER", "Chatter"
        SYSTEM = "SYSTEM", "System"

    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"
        PPV = "PPV", "PPV"

    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    sender_type = models.CharField(max_length=20, choices=SenderType.choices)
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="sent_messages",
        on_delete=models.SET_NULL,
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT,
    )
    text = models.TextField()
    ppv_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    client_message_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["conversation", "id"]),
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender_type", "created_at"]),
            models.Index(fields=["client_message_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "client_message_id"],
                condition=models.Q(client_message_id__isnull=False),
                name="unique_client_message_per_conversation",
            ),
        ]

    def __str__(self) -> str:
        short_text = self.text[:50] + ("..." if len(self.text) > 50 else "")
        return f"#{self.conversation_id} {self.sender_type}: {short_text}"

    def clean(self):
        super().clean()
        errors = {}

        if self.message_type == self.MessageType.PPV:
            if self.ppv_price is None or self.ppv_price <= Decimal("0"):
                errors["ppv_price"] = "PPV messages must have a price greater than 0."
        elif self.message_type == self.MessageType.TEXT:
            if self.ppv_price is not None:
                errors["ppv_price"] = "Text messages must not have a PPV price."

        if self.sender_type == self.SenderType.CHATTER:
            if self.sender_user is None:
                errors["sender_user"] = "Chatter messages must have a sender user."
        elif self.sender_type == self.SenderType.FAN:
            if self.sender_user is not None:
                errors["sender_user"] = "Fan messages must not have a sender user."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ConversationReadState(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name="read_states",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="conversation_read_states",
        on_delete=models.CASCADE,
    )
    last_read_message = models.ForeignKey(
        Message,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    last_read_at = models.DateTimeField(null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"],
                name="unique_read_state_per_conversation_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "unread_count"]),
            models.Index(fields=["conversation", "user"]),
        ]

    def __str__(self) -> str:
        return f"Conversation #{self.conversation_id} / {self.user} ({self.unread_count} unread)"


class ResponseTimer(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        ANSWERED = "ANSWERED", "Answered"

    conversation = models.ForeignKey(
        Conversation,
        related_name="response_timers",
        on_delete=models.CASCADE,
    )
    started_by_message = models.ForeignKey(
        Message,
        related_name="started_response_timers",
        on_delete=models.PROTECT,
    )
    stopped_by_message = models.ForeignKey(
        Message,
        related_name="stopped_response_timers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField(null=True, blank=True)
    response_seconds = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["conversation", "status"]),
            models.Index(fields=["status", "started_at"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self) -> str:
        return f"Conversation #{self.conversation_id} ({self.status})"

    def clean(self):
        super().clean()
        errors = {}

        if self.status == self.Status.ANSWERED and self.stopped_at is None:
            errors["stopped_at"] = "Answered timers must have a stopped_at value."

        if self.stopped_at is not None and self.started_at is not None:
            if self.stopped_at < self.started_at:
                errors["stopped_at"] = "stopped_at cannot be earlier than started_at."

        if self.response_seconds is not None and self.response_seconds < 0:
            errors["response_seconds"] = "response_seconds must be non-negative."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
