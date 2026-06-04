from django.urls import path

from apps.accounts.admin_views import (
    AdminInviteListCreateView,
    AdminInviteRevokeView,
    AdminUserActivateView,
    AdminUserDeactivateView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<int:pk>/update/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("users/<int:pk>/deactivate/", AdminUserDeactivateView.as_view(), name="admin-user-deactivate"),
    path("users/<int:pk>/activate/", AdminUserActivateView.as_view(), name="admin-user-activate"),
    path("invites/", AdminInviteListCreateView.as_view(), name="admin-invite-list-create"),
    path("invites/<int:pk>/revoke/", AdminInviteRevokeView.as_view(), name="admin-invite-revoke"),
]
