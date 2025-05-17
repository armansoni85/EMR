# importing the drf libraries
from rest_framework import serializers

# importing from the base
from base.utils import get_current_datetime

# importing from the app
from .models import Appointment
from user.serializers import UserListSerializers
from user.choices import RoleType

# importing from the strings
from strings import (
    PATIENT_DOCTOR_HOSPITAL_DIFFERENT,
    APPOINTMENT_ALREADY_BOOKED,
    APPOINTMENT_PAST_DATE,
)


class AppointmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            "id",
            "doctor",
            "patient",
            "appointment_datetime",
            "reason_of_visit",
            "disease",
            "appointment_status",
        )
        read_only_fields = [
            "id",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "patient",
            "reason_of_visit",
            "appointment_datetime",
            "disease",
            "appointment_status",
        ]
        read_only_fields = ["id", "patient"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["patient"] = UserListSerializers(instance.patient).data
        data["doctor"] = UserListSerializers(instance.doctor).data
        return data

    def validate(self, attrs):
        data = super().validate(attrs)
        doctor = data.get("doctor")
        request = self.context["request"]
        user = request.user
        user_role = user.role
        instance = self.instance
        if user_role == RoleType.patient.value[0]:
            data["patient"] = user

        method = request.method
        if method == "PUT":
            doctor = instance.doctor
            data["appointment_datetime"] = instance.appointment_datetime
            if user_role != RoleType.doctor.value[0]:
                data.pop("appointment_status", None)

        # validate doctor and patient is of same hospital
        if doctor.hospital_id != user.hospital_id:
            raise serializers.ValidationError(PATIENT_DOCTOR_HOSPITAL_DIFFERENT)

        # # validate appointment datetime cannot be in past
        if get_current_datetime() > data["appointment_datetime"]:
            raise serializers.ValidationError(APPOINTMENT_PAST_DATE)

        if method == "POST":
            # check if appointment date is already booked
            if Appointment.objects.filter(
                appointment_datetime=data["appointment_datetime"], doctor_id=doctor
            ).exists():
                raise serializers.ValidationError(APPOINTMENT_ALREADY_BOOKED)

        return data
