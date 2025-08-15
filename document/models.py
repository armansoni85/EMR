from django.conf import settings
from django.db import models
from base.base_models import BaseModel
from base.base_upload_handlers import (
    handle_medical_document_upload_limit,
    handle_medical_document,
)
from base.utils import validate_medical_document_extension
from django.utils.translation import gettext as _
from document.choices import DepartmentChoices


class MedicalDocument(BaseModel):
    file_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("File Name")
    )
    file = models.FileField(
        validators=[
            validate_medical_document_extension,
            handle_medical_document_upload_limit,
        ],
        upload_to=handle_medical_document,
        verbose_name=_("File"),
    )
    belonging_department = models.CharField(
        max_length=50,
        choices=[x.value for x in DepartmentChoices],
        verbose_name=_("Belonging Department"),
        help_text=_("Select the department this document is associated with."),
    )
    note = models.CharField(max_length=255, verbose_name="Note", null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="documents_uploaded",
        verbose_name="Uploaded By",
    )

    uploaded_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="documents_received",
        verbose_name="Uploaded To",
    )

    class Meta:
        verbose_name = "MedicalDocument"
        verbose_name_plural = "MedicalDocuments"

    def __str__(self):
        return self.file.name if self.file else "No file uploaded"
