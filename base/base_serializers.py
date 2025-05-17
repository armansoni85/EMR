from rest_framework import serializers
import uuid
from strings import (
    INVALID_CONTENT_TYPE,
)
from django.utils.translation import gettext as _


class CustomUUIDField(serializers.CharField):
    def to_internal_value(self, data):
        return super().to_internal_value(data)


class UploadFileSerializers(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        if value.content_type != "text/csv":
            raise serializers.ValidationError(INVALID_CONTENT_TYPE.format("text/csv"))

        return value
