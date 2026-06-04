from rest_framework import serializers


class MonitorChatterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField()
    role = serializers.CharField()
    is_online = serializers.BooleanField()
    active_conversations_count = serializers.IntegerField()
    waiting_conversations_count = serializers.IntegerField()
    overdue_conversations_count = serializers.IntegerField()
    last_seen_at = serializers.DateTimeField(allow_null=True)
