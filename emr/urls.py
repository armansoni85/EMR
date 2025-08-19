import os
import re

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

admin.site.site_header = "EMR"
admin.site.site_url = None
from django.conf.urls.static import static


schema_view = get_schema_view(
    openapi.Info(
        title="EMR",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # path("admin/", admin.site.urls),
    path(settings.ADMIN_PANEL_URL, admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "api/v1/users/",
        include("user.urls"),
    ),
    path(
        "api/v1/hospitals/",
        include("hospital.urls"),
    ),
    path(
        "api/v1/employee/",
        include("employee.urls"),
    ),
    path(
        "api/v1/dashboard/",
        include("dashboard.urls"),
    ),
    path(
        "api/v1/Notes/",
        include("Notes.urls"),
    ),
    path(
        "api/v1/appointments/",
        include("appointments.urls"),
    ),
    path(
        "api/v1/consultations/",
        include("consultation.urls"),
    ),
    path(
        "api/v1/superbills/",
        include("superbills.urls"),
    ),
    path("api/v1/prescriptions/", include("prescription.urls")),
    path(
        "api/v1/medical-documents/",
        include("document.urls"),
    ),
    path("api/v1/support/", include("support.urls")),
    # path("api/v1/notifications/", include("notification.urls")),
    # path("api/v1/logs/", include("api_log.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
