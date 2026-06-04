from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import UserInvite, UserProfile


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


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    display_name = serializers.CharField(source="profile.display_name", read_only=True)
    last_seen_at = serializers.DateTimeField(source="profile.last_seen_at", read_only=True)
    profile_created_at = serializers.DateTimeField(source="profile.created_at", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "role",
            "display_name",
            "last_seen_at",
            "profile_created_at",
        ]


class AdminUserUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=UserProfile.Role.choices,
        required=False,
    )
    display_name = serializers.CharField(max_length=255, required=False)
    is_active = serializers.BooleanField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context.get("request")
        target_user = self.context.get("target_user")
        if request is None or target_user is None:
            return attrs

        if target_user.pk == request.user.pk:
            if attrs.get("is_active") is False:
                raise serializers.ValidationError(
                    {"is_active": "You cannot deactivate your own account."}
                )
            new_role = attrs.get("role")
            if new_role is not None and new_role != UserProfile.Role.ADMIN:
                raise serializers.ValidationError(
                    {"role": "You cannot remove your own ADMIN role."}
                )

        return attrs

    def update(self, instance, validated_data):
        profile = instance.profile
        profile_updated = False

        if "email" in validated_data:
            instance.email = validated_data["email"]
        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]
        if "role" in validated_data:
            profile.role = validated_data["role"]
            profile_updated = True
        if "display_name" in validated_data:
            profile.display_name = validated_data["display_name"]
            profile_updated = True

        instance.save()
        if profile_updated:
            profile.save()

        return instance


class InviteUserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserInviteSerializer(serializers.ModelSerializer):
    invited_by = InviteUserSummarySerializer(read_only=True)
    accepted_by = InviteUserSummarySerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_accepted = serializers.BooleanField(read_only=True)
    is_active_invite = serializers.BooleanField(read_only=True)
    invite_url = serializers.SerializerMethodField()

    class Meta:
        model = UserInvite
        fields = [
            "id",
            "token",
            "email",
            "role",
            "invited_by",
            "accepted_by",
            "is_revoked",
            "expires_at",
            "accepted_at",
            "created_at",
            "is_expired",
            "is_accepted",
            "is_active_invite",
            "invite_url",
        ]

    def get_invite_url(self, obj) -> str:
        base_url = settings.FRONTEND_BASE_URL.rstrip("/")
        return f"{base_url}/invite/{obj.token}"


class CreateUserInviteSerializer(serializers.ModelSerializer):
    expires_in_hours = serializers.IntegerField(default=72, min_value=1, max_value=720, write_only=True)

    class Meta:
        model = UserInvite
        fields = ["email", "role", "expires_in_hours"]

    def validate_role(self, value):
        if value not in UserInvite.INVITE_ROLES:
            raise serializers.ValidationError("Invite role must be CHATTER or TEAMLEAD.")
        return value

    def create(self, validated_data):
        expires_in_hours = validated_data.pop("expires_in_hours", 72)
        request = self.context["request"]
        return UserInvite.objects.create(
            email=validated_data.get("email", ""),
            role=validated_data.get("role", UserProfile.Role.CHATTER),
            invited_by=request.user,
            expires_at=timezone.now() + timezone.timedelta(hours=expires_in_hours),
        )


class PublicInviteSerializer(serializers.ModelSerializer):
    is_active_invite = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = UserInvite
        fields = ["token", "email", "role", "expires_at", "is_active_invite", "status"]


class AcceptInviteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    display_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        invite: UserInvite = self.context["invite"]
        username = attrs["username"]
        email = (attrs.get("email") or "").strip()
        password = attrs["password"]
        password_confirm = attrs["password_confirm"]

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        if not invite.is_active_invite:
            raise serializers.ValidationError(
                {"detail": f"Invite is not active (status: {invite.status})."}
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

        if invite.email:
            if email and email.lower() != invite.email.lower():
                raise serializers.ValidationError(
                    {"email": "Email must match the invited email address."}
                )
            attrs["resolved_email"] = invite.email
        else:
            if not email:
                raise serializers.ValidationError({"email": "Email is required."})
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})
            attrs["resolved_email"] = email

        try:
            validate_password(
                password,
                User(username=username, email=attrs.get("resolved_email", "")),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        invite: UserInvite = self.context["invite"]
        username = validated_data["username"]
        password = validated_data["password"]
        display_name = validated_data.get("display_name") or username
        email = validated_data.get("resolved_email", "")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        profile = user.profile
        profile.role = invite.role
        profile.display_name = display_name
        profile.save(update_fields=["role", "display_name"])

        invite.accepted_by = user
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_by", "accepted_at", "updated_at"])

        return user


class AcceptedUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    display_name = serializers.CharField(source="profile.display_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "display_name", "is_active", "date_joined"]
