from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from base.utils import random_password
from .forms import (
    CustomUserCreationForm,
    # CustomGroupForm
)
from base.base_admin import BaseAdmin
from .models import (
    CustomUser,
    DeviceToken,
    UserLoginSession,
    PasswordResetToken,
    UserPermission,
)
from .choices import RoleType

# from .tasks import send_mail_task #open it when mail task is added
from django.db import transaction
from django.utils.translation import gettext as _


admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    # "phone_number_1",
                    # "phone_number_2",
                )
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "country",
                    "hospital",
                    "is_blocked",
                    "auto_unblock_at",
                    "login_attempts_failed_count",
                    "last_login_failed_at",
                    "is_mobile_push_notification_enable",
                    "is_web_push_notification_enable",
                    "is_email_notification_enable",
                    "notification_setting",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "role"),
            },
        ),
        # ('Company and store/location', {
        #     'fields': ('company', 'store'),
        # }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "country",
                    # "phone_number_1",
                    # "phone_number_2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                ),
            },
        ),
    )
    add_form = CustomUserCreationForm

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_blocked",
        'created_by'
    )
    list_filter = (
        "is_superuser",
        "is_active",
        "is_blocked",
        "is_mobile_push_notification_enable",
        "is_web_push_notification_enable",
        "is_email_notification_enable",
        "notification_setting",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    ordering = ("first_name",)
    exclude = ["is_deleted", "deleted_at"]


@admin.register(DeviceToken)
class DeviceTokenAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(DeviceTokenAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    list_display = ["user", "jwt_refresh_token_expiry_timestamp"]
    search_fields = ("token", "user__email")


@admin.register(UserLoginSession)
class UserLoginSessionAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(UserLoginSessionAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    readonly_fields = ["session_id", "session_expired_at", "ip_address", "user"]

    list_display = ["session_id", "session_expired_at", "ip_address", "user"]
    search_fields = (
        "ip_address",
        "session_id",
        "user__email",
        "session_expired_at",
    )

    @admin.display(description="IP Address")
    def ip_address(self, obj):
        return obj.remote_address


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(PasswordResetTokenAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    list_display = ["user", "is_token_used"]
    search_fields = ("user__email",)
    list_filter = ("is_token_used",)

    @admin.display(description="User Email")
    def user(self, obj):
        return obj.email


@admin.register(UserPermission)
class UserPermissionAdmin(BaseAdmin):
    def get_queryset(self, request):
        queryset = super(UserPermissionAdmin, self).get_queryset(request)
        return queryset.select_related("user")

    list_display = ["user", "permission_name"]
    search_fields = ("user__email",)
    list_filter = ("permission_type",)

    @admin.display(description="User Email")
    def user(self, obj):
        return obj.email

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True