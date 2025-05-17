from django.core.exceptions import ValidationError
from strings import RATING_VALIDATION_ERROR

def validate_hospital_rating(value):
    if value>5:
        raise ValidationError(RATING_VALIDATION_ERROR)