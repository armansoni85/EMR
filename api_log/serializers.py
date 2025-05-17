from rest_framework import serializers
from api_log.models import APIRequestLog
from user.serializers import UserListSerializers
from datetime import datetime
from base.choices import (
    ATIONETActionOption,
    ATIONETSubCategoryOptions,
    ATIONETCategoryOptions,
)
from base.base_serializers import ReportDownloadSearchSerializer


class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = (
            "id",
            "endpoint",
            "response_code",
            "method",
            "remote_address",
            "exec_time",
            "body_response",
            "body_request",
            "is_mobile",
            "is_touch_capable",
            "is_tablet",
            "is_pc",
            "is_bot",
            "browser_family",
            "browser_version",
            "os_family",
            "os_version",
            "device_family",
            "user",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, "user"):
            data["user"] = UserListSerializers(instance=instance.user).data
        return data


class DownloadATIONETAPILogSerializers(serializers.Serializer):
    user_id = serializers.UUIDField(required=False)
    category = serializers.ChoiceField(
        required=False, choices=[x.value for x in ATIONETCategoryOptions]
    )
    specific_date = serializers.DateField()
    company_id = serializers.UUIDField(required=False)
    action = serializers.ChoiceField(
        required=False, choices=[x.value for x in ATIONETActionOption]
    )
    sub_category = serializers.ChoiceField(
        required=False, choices=[x.value for x in ATIONETSubCategoryOptions]
    )
