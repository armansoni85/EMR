import os
from django.db import models
from base.base_models import BaseModel
from django.utils.translation import gettext as _
from user.models import CustomUser
from base.base_upload_handlers import (
    handle_qualification_document,
    handle_certification_document,
    handle_file_upload_limit,
)
from base.utils import validate_document_extension, delete_media


class ProfessionalInformation(BaseModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="professional_informations"
    )
    speciality = models.CharField(max_length=200, verbose_name=_("Speciality"))
    sub_speciality = models.CharField(max_length=200, verbose_name=_("Sub Speciality"))
    medical_license_number = models.CharField(
        max_length=100, verbose_name=_("Medical License Number")
    )
    years_of_experience = models.FloatField(
        verbose_name=_("Experienced Year"), null=True, blank=True
    )
    profession_id = models.CharField(unique=True, verbose_name=_("Profession Id"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "ProfessionalInformation"
        verbose_name = "ProfessionalInformations"

    def __str__(self):
        return f"{self.user.email} - {self.speciality}"


class DutyDetail(BaseModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="duty_details"
    )
    department_name = models.CharField(max_length=100, verbose_name=_("Department"))
    duty_start_time = models.TimeField(verbose_name=_("Duty Start Time"))
    duty_end_time = models.TimeField(verbose_name=_("Duty End Time"))
    is_on_call = models.BooleanField(verbose_name=_("On call availability"))
    room_number = models.CharField(max_length=50, verbose_name=_("Consultation Room"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "DutyDetail"
        verbose_name = "DutyDetails"

    def __str__(self):
        return f"{self.user.email} - {self.department_name}-{self.room_number}"


class Qualification(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        related_name="qualifications",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Qualification Name"))
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    organization = models.CharField(
        max_length=100, verbose_name=_("Granting Organization")
    )
    document = models.FileField(
        upload_to=handle_qualification_document,
        validators=[validate_document_extension, handle_file_upload_limit],
    )

    class Meta:
        verbose_name = _("Qualification")
        verbose_name_plural = _("Qualifications")

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # once queryset is deleted, delete the document image from the storage
        if self.document:
            delete_media(self.document.name)
        super().delete(*args, **kwargs)


class Certification(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        related_name="certifications",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Certification Name"))
    issued_by = models.CharField(max_length=100, verbose_name=_("Issued By"))
    valid_until = models.DateField(verbose_name=_("Valid Until"), blank=True, null=True)
    document = models.FileField(
        upload_to=handle_certification_document,
        validators=[validate_document_extension, handle_file_upload_limit],
    )

    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # once queryset is deleted, delete the document image from the storage
        if self.document:
            delete_media(file_directory=self.document.name)
        super().delete(*args, **kwargs)
