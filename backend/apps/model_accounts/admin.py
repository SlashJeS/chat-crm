from django.contrib import admin

from apps.model_accounts.models import ModelAccount


@admin.register(ModelAccount)
class ModelAccountAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
