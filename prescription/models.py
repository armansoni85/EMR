from django.db import models
import uuid
from django.conf import settings

class Prescription(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_prescriptions",
        help_text="Must be a user with patient role",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_prescriptions",
        help_text="Must be a user with doctor role",
    )
    disease = models.CharField(max_length=255)
    pharmacy_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Prescription {self.id} for {self.patient.email}"


class PrescriptionItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
    )
    medicine_name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True)
    quantity = models.CharField(max_length=50)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medicine_name} ({self.prescription.id})"

