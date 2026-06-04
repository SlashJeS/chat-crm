from django.contrib import admin

from apps.accounts.models import UserInvite, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "display_name", "created_at", "updated_at"]
    list_filter = ["role"]
    search_fields = ["user__username", "display_name"]


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = [
        "token",
        "email",
        "role",
        "invited_by",
        "accepted_by",
        "is_revoked",
        "expires_at",
        "accepted_at",
        "created_at",
    ]
    list_filter = ["role", "is_revoked", "accepted_at", "expires_at"]
    search_fields = [
        "email",
        "invited_by__username",
        "invited_by__email",
        "accepted_by__username",
        "accepted_by__email",
    ]
    readonly_fields = ["token", "accepted_at", "created_at", "updated_at"]
