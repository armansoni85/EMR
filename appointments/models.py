from django.utils.translation import gettext as _
from django.conf import settings  # To use CustomUser model
from django.db import models
from base.base_models import BaseModel
from .validators import validate_doctor, validate_patient
from .choices import AppointmentStatus


class Appointment(BaseModel):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        verbose_name=_("Doctor"),
        validators=[validate_doctor],
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        verbose_name=_("Patient"),
        validators=[validate_patient],
    )
    appointment_datetime = models.DateTimeField(verbose_name=_("Appointment Date"))
    reason_of_visit = models.TextField(verbose_name=_("Reason of visit"))
    disease = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Disease")
    )
    appointment_status = models.CharField(
        default=AppointmentStatus.pending.value[0],
        choices=[x.value for x in AppointmentStatus],
        verbose_name=_("Appointment Status"),
    )

    def __str__(self):
        return f"Appointment: {self.patient.email} with {self.doctor.email} on {self.created_at} status is {self.appointment_status}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ["-created_at"]
