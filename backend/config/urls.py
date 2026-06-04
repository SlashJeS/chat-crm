from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.conversations.views import SimulateFanMessageView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.urls")),
    path("api/conversations/", include("apps.conversations.urls")),
    path("api/monitor/", include("apps.monitoring.urls")),
    path("api/dev/simulate-fan-message/", SimulateFanMessageView.as_view(), name="simulate-fan-message"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
