from django.contrib.auth.models import User
from rest_framework import serializers

from apps.conversations.models import Conversation, ConversationReadState, Fan, Message
from apps.model_accounts.models import ModelAccount


class FanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fan
        fields = ["id", "external_id", "display_name", "avatar_url"]


class ModelAccountShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelAccount
        fields = ["id", "name", "avatar_url"]


class UserShortSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="profile.display_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "display_name"]


class MessageSerializer(serializers.ModelSerializer):
    sender_user = UserShortSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender_type",
            "sender_user",
            "message_type",
            "text",
            "ppv_price",
            "client_message_id",
            "created_at",
        ]


class ConversationReadStateSerializer(serializers.ModelSerializer):
    last_read_message = MessageSerializer(read_only=True)

    class Meta:
        model = ConversationReadState
        fields = ["last_read_message", "last_read_at", "unread_count"]


class ConversationListSerializer(serializers.ModelSerializer):
    fan = FanSerializer(read_only=True)
    model_account = ModelAccountShortSerializer(read_only=True)
    assigned_chatter = UserShortSerializer(read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "fan",
            "model_account",
            "assigned_chatter",
            "status",
            "last_message",
            "last_message_at",
            "unread_count",
            "waiting_since",
            "last_fan_message_at",
            "last_chatter_message_at",
            "is_overdue",
        ]

    def get_unread_count(self, obj):
        read_states = getattr(obj, "current_user_read_states", None)
        if read_states:
            return read_states[0].unread_count
        user = self.context.get("user")
        if user is not None:
            read_state = obj.read_states.filter(user=user).first()
            return read_state.unread_count if read_state else 0
        return 0

    def get_is_overdue(self, obj):
        from apps.conversations.selectors import is_conversation_overdue

        return is_conversation_overdue(obj)


class ConversationDetailSerializer(ConversationListSerializer):
    class Meta(ConversationListSerializer.Meta):
        fields = ConversationListSerializer.Meta.fields + ["created_at", "updated_at"]
