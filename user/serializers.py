import json
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser
from django.utils.translation import gettext as _
from base.utils import (
    custom_password_validator,
)
from strings import *
from django_countries.serializers import CountryFieldMixin
from hospital.serializers import HospitalListSerializer


class CustomPasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        self.required = False
        self.allow_blank = True
        self.allow_null = True
        self.validators.append(custom_password_validator)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        data = make_password(data)
        return super().to_internal_value(data)


class CustomEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        data = data.lower()
        return super().to_internal_value(data)


class UserPasswordSerializer(serializers.ModelSerializer):
    password = CustomPasswordField(required=True)

    class Meta:
        model = CustomUser
        fields = ("password",)


class UserCodeAndTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=200, help_text=_("Put the token recieved in the email")
    )
    otp = serializers.CharField(max_length=20)

    class Meta:
        model = CustomUser
        fields = ("token", "otp")


class UserPasswordCodeAndTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=200, help_text=_("Put the token recieved in the email")
    )
    otp = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=25)

    class Meta:
        model = CustomUser
        fields = ("token", "otp", "password")


class MobileUserPasswordAndCodeAndTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=200,
        help_text=_(
            "Put the token received  in the API Response while requesting for password-reset."
        ),
    )
    otp = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=50)

    class Meta:
        model = CustomUser
        fields = ("token", "otp", "password")


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    password = CustomPasswordField(required=True)
    old_password = CustomPasswordField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            "old_password",
            "password",
        )


class LoginSerializer(serializers.Serializer):
    email = CustomEmailField(
        max_length=254,
    )
    password = serializers.CharField(
        max_length=100,
    )
    fmc_registration_token = serializers.CharField(max_length=300, required=False)
    device_type = serializers.CharField(max_length=100, required=False)


class InputOnlyField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class UserLogoutSerializers(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class CreatedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "email")


class CustomUserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    email = CustomEmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(), message=EMAIL_EXISTS, lookup="iexact"
            )
        ],
    )
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "date_joined",
            "first_name",
            "profile_picture",
            "last_name",
            "email",
            "hospital",
            "role",
            "country",
            "last_login",
            "is_active",
            "is_blocked",
            "password",
            "confirm_password",
            "created_by",
            "disease",
            "height_feet",
            "height_inches",
            "weight_kilo",
            "weight_grams",

        )

        read_only_fields = ("date_joined", "created_by")
        write_only_fields = ("confirm_password",)

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        hospital = validated_data.get("hospital")
        password = validated_data.get("password")
        role = validated_data.get("role")
        confirm_password = validated_data.get("confirm_password")
        if self.context["request"].method == "POST":
            if not hospital:
                raise serializers.ValidationError("hospital required")
            if not password or not confirm_password:
                raise serializers.ValidationError(
                    "password or confirm-password cannot be empty."
                )
            if password.strip() != confirm_password.strip():
                raise serializers.ValidationError(
                    "password and confirm-password is different."
                )

            if not role:
                raise serializers.ValidationError("role is required")
        if password:
            validated_data["password"] = make_password(password.strip())
        validated_data.pop("confirm_password", None)
        return validated_data

    def create(self, validated_data):
        validated_data["is_active"] = True
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "password" in data.keys():
            del data["password"]
        if instance.country:
            data["country"] = instance.country.name
            data["flag"] = instance.country.flag
        if instance.hospital:
            data["hospital"] = HospitalListSerializer(instance.hospital).data
        if instance.created_by:
            data["created_by"] = CreatedBySerializer(instance.created_by).data
        return data


class UserListSerializers(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    flag = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "date_joined",
            "first_name",
            "profile_picture",
            "last_name",
            "email",
            "role",
            "country",
            "flag",
            "gender",
            "dob",
            "phone_number",
            "last_login",
            "is_active",
            "is_blocked",
        )

    def get_country(self, instance):
        return instance.country.name if instance.country else None

    def get_flag(self, instance):
        return instance.country.flag if instance.country else None
