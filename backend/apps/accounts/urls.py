from django.urls import path

from apps.accounts.invite_views import AcceptInviteView, PublicInviteDetailView
from apps.accounts.views import HealthView, MeView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("me/", MeView.as_view(), name="me"),
    path("invites/<uuid:token>/", PublicInviteDetailView.as_view(), name="public-invite-detail"),
    path("invites/<uuid:token>/accept/", AcceptInviteView.as_view(), name="accept-invite"),
]
