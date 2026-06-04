from django.contrib import admin

from apps.conversations.models import (
    Conversation,
    ConversationReadState,
    Fan,
    Message,
    ResponseTimer,
)


@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ["display_name", "external_id", "created_at", "updated_at"]
    search_fields = ["display_name", "external_id"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "fan",
        "model_account",
        "assigned_chatter",
        "status",
        "last_message_at",
        "waiting_since",
    ]
    list_filter = ["status", "model_account"]
    search_fields = ["fan__display_name", "fan__external_id", "model_account__name"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["fan", "model_account", "assigned_chatter", "last_message"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "conversation",
        "sender_type",
        "message_type",
        "text",
        "ppv_price",
        "created_at",
    ]
    list_filter = ["sender_type", "message_type"]
    search_fields = ["text", "client_message_id"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["conversation", "sender_user"]


@admin.register(ConversationReadState)
class ConversationReadStateAdmin(admin.ModelAdmin):
    list_display = [
        "conversation",
        "user",
        "unread_count",
        "last_read_at",
        "updated_at",
    ]
    list_filter = ["unread_count"]
    search_fields = ["user__username", "conversation__fan__display_name"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["conversation", "user", "last_read_message"]


@admin.register(ResponseTimer)
class ResponseTimerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "conversation",
        "status",
        "started_at",
        "stopped_at",
        "response_seconds",
    ]
    list_filter = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["conversation", "started_by_message", "stopped_by_message"]
