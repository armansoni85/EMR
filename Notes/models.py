from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings  # To use CustomUser model
from appointments.validators import validate_doctor, validate_patient

class Note(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_notes",
        verbose_name=_("Doctor"),
        validators=[validate_doctor])
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_notes",
        verbose_name=_("Patient"),
        validators=[validate_patient], default="")
    subjective = models.CharField(max_length=255)
    cc = models.CharField(max_length=255)
    allergies = models.CharField(max_length=255, blank=True, null=True)
    vitals = models.CharField(max_length=255, blank=True, null=True)
    plan = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subjective} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"
