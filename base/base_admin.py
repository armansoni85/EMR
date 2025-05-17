from django.contrib import admin
from django.conf import settings


class BaseAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    exclude = ["deleted_at", "is_deleted"]

    readonly_fields = ("created_at", "modified_at")

    def has_add_permission(self, request, obj=None):
        return True if settings.DEBUG_ADMIN_PANEL else False

    def has_change_permission(self, request, obj=None):
        return True if settings.DEBUG_ADMIN_PANEL else False

    def has_delete_permission(self, request, obj=None):
        return True if settings.DEBUG_ADMIN_PANEL else False
