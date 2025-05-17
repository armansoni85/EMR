from django.urls import path
from notification.views import (
    EnableDisableNotificationView,
    NotificationView,
)

urlpatterns = [
    path(
        "push-notification-config/",
        EnableDisableNotificationView.as_view({"get": "list"}),
        name="register-device-token-list",
    ),
    path(
        "push-notification-config/<str:pk>/",
        EnableDisableNotificationView.as_view({"put": "update"}),
        name="register-device-token-detail",
    ),
    path(
        "",
        NotificationView.as_view({"get": "list"}),
        name="notifications",
    ),
    path(
        "<str:pk>/",
        NotificationView.as_view({"put": "update", "get": "retrieve"}),
        name="notifications-detail",
    ),
]
