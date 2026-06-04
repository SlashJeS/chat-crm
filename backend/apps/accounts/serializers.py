from django.contrib.auth.models import User
from rest_framework import serializers

from apps.accounts.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["role", "display_name"]


class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    display_name = serializers.CharField(source="profile.display_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "display_name"]
