from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from user.choices import RoleType


def validate_doctor(value):
    if value.role != RoleType.doctor.value[0]:
        raise ValidationError(
            _("%(value)s is not a doctor"),
            params={"value": value},
        )


def validate_patient(value):
    if value.role != RoleType.patient.value[0]:
        raise ValidationError(
            _("%(value)s is not a patient"),
            params={"value": value},
        )
