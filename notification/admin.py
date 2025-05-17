from django.contrib import admin
from base.base_admin import BaseAdmin
from notification.models import NotificationSent


# Register your models here.
@admin.register(NotificationSent)
class NotificationSentAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(NotificationSentAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    list_display = ["title", "is_sent", "notification_type", "user"]
    search_fields = ("title", "user__email")
    list_filter = ("notification_type", "is_sent", "device_type")
