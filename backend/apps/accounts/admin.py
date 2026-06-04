from django.contrib import admin

from apps.accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "display_name", "created_at", "updated_at"]
    list_filter = ["role"]
    search_fields = ["user__username", "display_name"]
