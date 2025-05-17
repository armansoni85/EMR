from django.db import models
from base.base_models import BaseModel
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator, RegexValidator
from django_countries.fields import CountryField
from base.base_upload_handlers import (
    handle_image_upload_limit,
    handle_hospital_logo,
)
from ckeditor.fields import RichTextField
from hospital.choices import HospitalType
from hospital.validators import validate_hospital_rating
from base.utils import delete_media


class Hospital(BaseModel):
    name = models.CharField(max_length=50, verbose_name=_("Hospital Name"))
    description = RichTextField(
        null=True, blank=True, verbose_name=_("Hospital motive and other details")
    )
    country = CountryField(verbose_name=_("Country"))
    logo = models.ImageField(
        validators=[handle_image_upload_limit],
        upload_to=handle_hospital_logo,
        verbose_name=_("Hospital Logo"),
        null=True,
        blank=True,
    )
    bed_capacity = models.IntegerField(
        verbose_name=_("Bed Capacity"), validators=[MinValueValidator(1)]
    )
    website_url = models.URLField(null=True, blank=True, verbose_name=_("Website Url"))
    city = models.CharField(max_length=50, verbose_name=_("City"))
    state = models.CharField(max_length=50, verbose_name=_("State"))
    contact_number = models.CharField(
        max_length=20,
        verbose_name=_("Contact Number"),
        validators=[RegexValidator(r"^\+?[0-9\s\-]+$")],
    )
    email_address = models.EmailField(verbose_name=_("Email Address"))
    hospital_type = models.CharField(
        max_length=50,
        choices=[x.value for x in HospitalType],
        default=HospitalType.general.value[0],
        verbose_name=_("Hospital Type"),
    )
    speciality = RichTextField(
        null=True, blank=True, verbose_name=_("Hospital Speciality")
    )
    established_date = models.DateField(verbose_name=_("Establised Date"))
    opening_time = models.TimeField(verbose_name=_("Opening Time"))
    closing_time = models.TimeField(verbose_name=_("Closing Time"))
    emergency_contact = models.CharField(
        max_length=20,
        verbose_name=_("Emergency Contact"),
        validators=[RegexValidator(r"^\+?[0-9\s\-]+$")],
    )
    ceo = models.CharField(max_length=50, verbose_name=_("Hospital CEO"))
    total_staff = models.IntegerField(
        verbose_name=_("Total Staff"), validators=[MinValueValidator(1)]
    )
    hospital_rating = models.FloatField(
        default=3,
        validators=[MinValueValidator(1), validate_hospital_rating],
        verbose_name=_("Hospital Rating"),
    )
    affiliation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Affiliated Hospital/Institution"),
    )
    facilities = RichTextField(verbose_name=_("Facilities"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Hospital"
        verbose_name = "Hospitals"

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        # once queryset is deleted, delete the logo image from the storage
        if self.logo:
            delete_media(self.logo.name)
        super().delete(*args, **kwargs)
