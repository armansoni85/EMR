# importing django models
from django.db import models

# importing base models
from base.base_models import BaseModel
from base.base_upload_handlers import (
    handle_consultation_recording,
    handle_consultation_recording_upload_limit,
)
from base.utils import validate_consultation_recording_extension,delete_media
from appointments.models import Appointment
from .choices import AIVoiceNoteStatus


class Consultation(BaseModel):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="consultations"
    )
    recording_ai_voice_note = models.TextField(
        null=True, blank=True, verbose_name="Recording AI Voice Note"
    )  # when doctor finishes the consultation then we will fill recording ai voice note
    recording_ai_voice_note_status = models.CharField(
        default=AIVoiceNoteStatus.rejected.value[0],
        choices=[x.value for x in AIVoiceNoteStatus],
        verbose_name="Recording AI Voice Note Status",
    )
    is_started = models.BooleanField(default=False, verbose_name="Is Started")
    is_finished = models.BooleanField(default=False, verbose_name="Is Finished")
    follow_up_date = models.DateField(
        null=True, blank=True, verbose_name="Follow Up Date"
    )

    class Meta:
        verbose_name_plural = "Consultations"
        verbose_name = "Consultation"
        ordering = ("-created_at",)


class ConsultationRecording(BaseModel):
    consultation = models.ForeignKey(
        Consultation, on_delete=models.CASCADE, related_name="consultation_recordings"
    )
    recording_audio = models.FileField(
        upload_to=handle_consultation_recording,
        validators=[
            handle_consultation_recording_upload_limit,
            validate_consultation_recording_extension,
        ],
        verbose_name="Recording",
    )

    class Meta:
        verbose_name_plural = "Consultation Recordings"
        verbose_name = "Consultation Recording"
        ordering = ("-created_at",)
    
    def delete(self, *args, **kwargs):
        # once queryset is deleted, delete the recording_audio from storage
        if self.recording_audio:
            delete_media(self.recording_audio.name)
        super().delete(*args, **kwargs)

