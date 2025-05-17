from django.urls import path
from .views import (
    AuditLogAtionetAPIView,
    APIRequestLogAPIView,
    DownloadMQGAPILogView,
    DownloadATIONETAPILogView,
)

urlpatterns = [
    path(
        "mqg/",
        APIRequestLogAPIView.as_view({"get": "list"}),
        name="api-request-log-list",
    ),
    path(
        "mqg/download-reports/",
        DownloadMQGAPILogView.as_view(),
        name="download-mqg-api-request-logs",
    ),
    path(
        "mqg/<str:pk>/",
        APIRequestLogAPIView.as_view({"get": "retrieve"}),
        name="api-request-log-detail",
    ),
    path(
        "ationet/",
        AuditLogAtionetAPIView.as_view({"get": "list"}),
        name="driver-ationet-list",
    ),
    path(
        "ationet/download-reports/",
        DownloadATIONETAPILogView.as_view(),
        name="download-ationet-api-request-logs",
    ),
    path(
        "ationet/<str:pk>/",
        AuditLogAtionetAPIView.as_view({"get": "retrieve"}),
        name="driver-ationet-detail",
    ),
]
