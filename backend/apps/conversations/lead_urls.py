from django.urls import path

from apps.conversations.lead_views import (
    LeadChatterWorkloadView,
    LeadConversationAssignView,
    LeadConversationDetailView,
    LeadConversationListView,
)

urlpatterns = [
    path("conversations/", LeadConversationListView.as_view(), name="lead-conversation-list"),
    path(
        "conversations/<int:pk>/",
        LeadConversationDetailView.as_view(),
        name="lead-conversation-detail",
    ),
    path(
        "conversations/<int:pk>/assign/",
        LeadConversationAssignView.as_view(),
        name="lead-conversation-assign",
    ),
    path("chatters/workload/", LeadChatterWorkloadView.as_view(), name="lead-chatter-workload"),
]
