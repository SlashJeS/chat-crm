from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserInvite, UserProfile
from apps.accounts.permissions import IsAdminRoleOnly
from apps.accounts.serializers import (
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    CreateUserInviteSerializer,
    UserInviteSerializer,
)


def _parse_limit_offset(query_params):
    try:
        limit = int(query_params.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 100))

    try:
        offset = int(query_params.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0
    offset = max(0, offset)

    return limit, offset


def _parse_optional_bool(value):
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    return None


def _admin_users_queryset():
    return User.objects.select_related("profile").order_by("-date_joined")


def _admin_invites_queryset():
    return UserInvite.objects.select_related("invited_by", "accepted_by").order_by("-created_at")


class AdminUserListView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def get(self, request):
        queryset = _admin_users_queryset()

        search = (request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(profile__display_name__icontains=search)
            )

        role = request.query_params.get("role")
        if role is not None:
            if role not in UserProfile.Role.values:
                return Response(
                    {"detail": "Invalid role filter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(profile__role=role)

        is_active = _parse_optional_bool(request.query_params.get("is_active"))
        if request.query_params.get("is_active") is not None and is_active is None:
            return Response(
                {"detail": "is_active must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        count = queryset.count()
        limit, offset = _parse_limit_offset(request.query_params)
        results = queryset[offset : offset + limit]

        serializer = AdminUserSerializer(results, many=True)
        return Response({"count": count, "results": serializer.data})


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def get(self, request, pk):
        user = _get_admin_user_or_404(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)


class AdminUserUpdateView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def patch(self, request, pk):
        user = _get_admin_user_or_404(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request, "target_user": user},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_user = serializer.update(user, serializer.validated_data)
        updated_user = _admin_users_queryset().get(pk=updated_user.pk)
        return Response(AdminUserSerializer(updated_user).data)


class AdminUserDeactivateView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def post(self, request, pk):
        user = _get_admin_user_or_404(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.pk == request.user.pk:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])
        user = _admin_users_queryset().get(pk=user.pk)
        return Response(AdminUserSerializer(user).data)


class AdminUserActivateView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def post(self, request, pk):
        user = _get_admin_user_or_404(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save(update_fields=["is_active"])
        user = _admin_users_queryset().get(pk=user.pk)
        return Response(AdminUserSerializer(user).data)


class AdminInviteListCreateView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def get(self, request):
        queryset = _admin_invites_queryset()

        role = request.query_params.get("role")
        if role is not None:
            if role not in UserProfile.Role.values:
                return Response(
                    {"detail": "Invalid role filter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(role=role)

        status_filter = request.query_params.get("status")
        if status_filter is not None:
            if status_filter == "active":
                queryset = queryset.filter(
                    is_revoked=False,
                    accepted_at__isnull=True,
                    expires_at__gt=timezone.now(),
                )
            elif status_filter == "accepted":
                queryset = queryset.filter(accepted_at__isnull=False)
            elif status_filter == "revoked":
                queryset = queryset.filter(is_revoked=True, accepted_at__isnull=True)
            elif status_filter == "expired":
                queryset = queryset.filter(
                    accepted_at__isnull=True,
                    is_revoked=False,
                    expires_at__lte=timezone.now(),
                )
            else:
                return Response(
                    {"detail": "status must be active, accepted, revoked, or expired."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        search = (request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(email__icontains=search)

        count = queryset.count()
        limit, offset = _parse_limit_offset(request.query_params)
        results = queryset[offset : offset + limit]

        serializer = UserInviteSerializer(results, many=True)
        return Response({"count": count, "results": serializer.data})

    def post(self, request):
        serializer = CreateUserInviteSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invite = serializer.save()
        invite = _admin_invites_queryset().get(pk=invite.pk)
        return Response(UserInviteSerializer(invite).data, status=status.HTTP_201_CREATED)


class AdminInviteRevokeView(APIView):
    permission_classes = [IsAdminRoleOnly]

    def post(self, request, pk):
        try:
            invite = _admin_invites_queryset().get(pk=pk)
        except UserInvite.DoesNotExist:
            return Response({"detail": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)

        if invite.is_accepted:
            return Response(
                {"detail": "Accepted invites cannot be revoked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not invite.is_revoked:
            invite.is_revoked = True
            invite.save(update_fields=["is_revoked", "updated_at"])

        return Response(UserInviteSerializer(invite).data)


def _get_admin_user_or_404(pk):
    try:
        return _admin_users_queryset().get(pk=pk)
    except User.DoesNotExist:
        return None
