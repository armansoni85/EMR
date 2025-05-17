from rest_framework import serializers
from notification.models import NotificationSent
from user.models import CustomUser


class EnableDisableNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "is_mobile_push_notification_enable",
            "is_web_push_notification_enable",
            "is_email_notification_enable",
            "notification_setting",
        ]

        read_only_fields = ("id",)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSent
        fields = [
            "id",
            "title",
            "body",
            "device_type",
            "notification_type",
            "is_notification_seen",
        ]

        read_only_fields = ("id", "title", "body", "device_type", "notification_type")
