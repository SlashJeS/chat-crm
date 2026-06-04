from rest_framework.permissions import BasePermission

from apps.accounts.models import UserProfile


class _RolePermission(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False
        return profile.role in self.allowed_roles


class IsChatter(_RolePermission):
    allowed_roles = (UserProfile.Role.CHATTER,)


class IsTeamlead(_RolePermission):
    allowed_roles = (UserProfile.Role.TEAMLEAD,)


class IsAdminRole(_RolePermission):
    allowed_roles = (UserProfile.Role.ADMIN,)


class IsTeamleadOrAdmin(_RolePermission):
    allowed_roles = (UserProfile.Role.TEAMLEAD, UserProfile.Role.ADMIN)
