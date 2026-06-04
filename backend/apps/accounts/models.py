import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    class Role(models.TextChoices):
        CHATTER = "CHATTER", "Chatter"
        TEAMLEAD = "TEAMLEAD", "Teamlead"
        ADMIN = "ADMIN", "Admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CHATTER,
    )
    display_name = models.CharField(max_length=255)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"


class UserInvite(models.Model):
    INVITE_ROLES = (
        UserProfile.Role.CHATTER,
        UserProfile.Role.TEAMLEAD,
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserProfile.Role.choices,
        default=UserProfile.Role.CHATTER,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invites",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invites",
    )
    is_revoked = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["role"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_revoked"]),
            models.Index(fields=["accepted_at"]),
        ]

    def __str__(self) -> str:
        return f"Invite {self.token} ({self.role})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_accepted(self) -> bool:
        return self.accepted_at is not None

    @property
    def is_active_invite(self) -> bool:
        return not self.is_revoked and not self.is_accepted and not self.is_expired

    @property
    def status(self) -> str:
        if self.is_accepted:
            return "accepted"
        if self.is_revoked:
            return "revoked"
        if self.is_expired:
            return "expired"
        return "active"
