# prescriptions/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Prescription, PrescriptionItem

User = get_user_model()


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = (
            "id",
            "medicine_name",
            "type",
            "quantity",
            "dosage",
            "frequency",
        )


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)

    # Accept any existing user UUID
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    doctor  = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Prescription
        fields = (
            "id",
            "patient",
            "doctor",
            "disease",
            "pharmacy_notes",
            "created_at",
            "items",
        )
        read_only_fields = ("created_at",)

    def validate_patient(self, value):
        # In your DB, "2" == patient
        if str(value.role) != "2":
            raise serializers.ValidationError("Selected user is not a Patient (role=2).")
        return value

    def validate_doctor(self, value):
        # In your DB, "3" == doctor
        if str(value.role) != "3":
            raise serializers.ValidationError("Selected user is not a Doctor (role=3).")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        return prescription

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PrescriptionItem.objects.create(prescription=instance, **item_data)
        return instance

