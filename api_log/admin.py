from django.contrib import admin
from api_log.models import APIRequestLog
from base.base_admin import BaseAdmin


# Register your models here.
@admin.register(APIRequestLog)
class APIRequestLogAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(APIRequestLogAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    list_display = [
        "remote_address",
        "endpoint",
        "method",
        "response_code",
        "user",
        "created_at",
    ]

    list_filter = ("method", "response_code", "created_at")
    search_fields = ("remote_address", "endpoint", "user__email", "created_at")
