# importing the drf library
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.db import transaction

# importing from base app
from base.utils import get_current_datetime

# importing the models from the consultation app
from .models import Consultation, ConsultationRecording
from appointments.models import Appointment
from appointments.choices import AppointmentStatus
from strings import OWN_APPOINTMENT_CONSULTATION_ONLY_ALLOWED, FOLLOW_UP_DATE_PAST


class ConsultationRecordingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRecording
        fields = ("id", "recording_audio")


class ConsultationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = [
            "id",
            "appointment",
            "recording_ai_voice_note",
            "recording_ai_voice_note_status",
            "is_started",
            "is_finished",
            "follow_up_date",
        ]
        read_only_fields = (
            "id",
            "is_started",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["recordings"] = ConsultationRecordingListSerializer(
            instance=instance.consultation_recordings.all(), many=True
        ).data
        return data


class ConsultationSerializer(ModelSerializer):
    class Meta:
        model = Consultation
        fields = [
            "id",
            "appointment",
            "recording_ai_voice_note",
            "recording_ai_voice_note_status",
            "is_started",
            "is_finished",
            "follow_up_date",
        ]
        read_only_fields = (
            "id",
            "is_started",
        )

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        follow_up_date = validated_data.get("follow_up_date")
        request = self.context["request"]
        appointment = validated_data.get(
            "appointment", self.instance.appointment if self.instance else None
        )

        if appointment.doctor_id != request.user.id:
            raise serializers.ValidationError(OWN_APPOINTMENT_CONSULTATION_ONLY_ALLOWED)

        if follow_up_date and follow_up_date < get_current_datetime().date():
            raise serializers.ValidationError(FOLLOW_UP_DATE_PAST)

        return validated_data

    def create(self, validated_data):
        # Set default value for `is_started`
        validated_data["is_started"] = True

        # Remove unnecessary keys if present in `validated_data`
        keys_to_remove = [
            "is_finished",
            "recording_ai_voice_note",
            "recording_ai_voice_note_status",
        ]
        for key in keys_to_remove:
            validated_data.pop(key, None)

        # Call the parent class's `create` method to finalize creation
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        # Remove `is_started` from validated data if present
        validated_data.pop("is_started", None)

        # Check if the update marks the consultation as finished
        is_finished = validated_data.get("is_finished")
        # Perform the update operation
        updated_instance = super().update(instance, validated_data)

        # If finished, update the associated appointment status to DONE
        if is_finished:
            Appointment.objects.filter(id=instance.appointment_id).update(
                appointment_status=AppointmentStatus.done.value[0]
            )

        return updated_instance


class ConsultationRecordingSerializer(ModelSerializer):
    class Meta:
        model = ConsultationRecording
        fields = ["id", "consultation", "recording_audio"]
        read_only_fields = ("id",)

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        if (
            validated_data["consultation"].appointment.doctor_id
            != self.context["request"].user.id
        ):
            raise serializers.ValidationError(OWN_APPOINTMENT_CONSULTATION_ONLY_ALLOWED)
        return validated_data
