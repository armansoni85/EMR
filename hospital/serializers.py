from rest_framework import serializers
from hospital.models import Hospital


class HospitalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = (
            "id",
            "name",
            "description",
            "logo",
            "contact_number",
            "bed_capacity",
            "country",
            "city",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.country:
            data["country"] = instance.country.name
            data["flag"] = instance.country.flag
        else:
            data["country"] = ""
            data["flag"] = ""

        return data


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = (
            "id",
            "name",
            "description",
            "logo",
            "bed_capacity",
            "contact_number",
            "bed_capacity",
            "website_url",
            "city",
            "state",
            "email_address",
            "hospital_type",
            "speciality",
            "established_date",
            "opening_time",
            "closing_time",
            "emergency_contact",
            "ceo",
            "total_staff",
            "hospital_rating",
            "affiliation",
            "facilities",
            "country",
        )
        read_only_fields = ("id",)

    def validate_country(self, value):

        if not value:
            raise serializers.ValidationError("country is required")
        return value

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.country:
            data["country"] = instance.country.name
            data["flag"] = instance.country.flag
        return data
