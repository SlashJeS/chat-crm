from django.urls import path

from apps.conversations.views import (
    ConversationDetailView,
    ConversationListView,
    ConversationMessagesView,
    ConversationReadView,
)

urlpatterns = [
    path("", ConversationListView.as_view(), name="conversation-list"),
    path("<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("<int:pk>/messages/", ConversationMessagesView.as_view(), name="conversation-messages"),
    path("<int:pk>/read/", ConversationReadView.as_view(), name="conversation-read"),
]
