from django.utils import timezone
from django.core.management.utils import get_random_string
from django.core.exceptions import ValidationError
from strings import *
import string
import random


def get_extension(filename):
    return f".{filename.split('.')[-1]}"


def get_random_name(filename):
    return f"{get_random_string(len(filename))}-{int(timezone.now().timestamp() * 1000)}{get_extension(filename)}"


def handle_tnc_document(instance, filename):
    new_filename = f"tnc/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_privacy_policy_document(instance, filename):
    new_filename = f"privacy_policy/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_user_profile_picture(instance, filename):
    new_filename = (
        f"users/profile-pictures/{instance.id.hex}/{get_random_name(filename)}"
    )
    return new_filename


def handle_medical_document(instance, filename):
    new_filename = f"documents/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_contract_document(instance, filename):
    new_filename = f"contract/documents/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_report_document(instance, filename):
    new_filename = f"{instance.id.hex}/{filename})"
    return new_filename


def handle_file_upload_limit(file):
    """
    Check if the size of the uploaded file exceeds the limit and raise a validation error if it does.

    Parameters:
        file (object): The uploaded file object.

    Raises:
        ValidationError: If the size of the file exceeds the limit.

    Returns:
        None
    """
    if file.size > 41943040:
        raise ValidationError(FILE_UPLOAD_LIMIT)


def handle_consultation_recording_upload_limit(file):
    """
    Check if the size of the uploaded file exceeds the limit and raise a validation error if it does.

    Parameters:
        file (object): The uploaded file object.

    Raises:
        ValidationError: If the size of the file exceeds the limit.

    Returns:
        None
    """
    if file.size > 41943040:
        raise ValidationError(FILE_UPLOAD_LIMIT)


def handle_image_upload_limit(file):
    """
    Handle image upload limit.

    Args:
        file (File): The file to be uploaded.

    Raises:
        ValidationError: If the file size exceeds the limit.

    Returns:
        None
    """
    if file.size > 41943040:
        raise ValidationError(FILE_UPLOAD_LIMIT)


def handle_consultation_recording_upload_limit(file):
    """
    Check if the size of the uploaded file exceeds the limit and raise a validation error if it does.

    Parameters:
        file (object): The uploaded file object.

    Raises:
        ValidationError: If the size of the file exceeds the limit.

    Returns:
        None
    """
    if file.size > 41943040:
        raise ValidationError(FILE_UPLOAD_LIMIT)


def handle_medical_document_upload_limit(file):
    """
    Handle medical document upload limit.

    Args:
        file (File): The file to be uploaded.

    Raises:
        ValidationError: If the file size exceeds the 25MB limit.
    """
    if file.size > 26214400:  # 25MB
        raise ValidationError(LIMITED_FILE_ALLOWED_EXTENSIONS)


def handle_payment_term_document(instance, filename):
    new_filename = f"payment_term/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def get_unique_id(length):
    custom_characters = string.ascii_letters + string.digits
    return "".join(random.choice(custom_characters) for _ in range(length))


def handle_master_file_data(instance, filename):
    new_filename = f"masterdata/files/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_hospital_logo(instance, filename):
    new_filename = f"hospital_logo/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_qualification_document(instance, filename):
    new_filename = f"qualification/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_certification_document(instance, filename):
    new_filename = f"certification/{instance.id.hex}/{get_random_name(filename)}"
    return new_filename


def handle_consultation_recording(instance, filename):
    new_filename = (
        f"consultation_recording/{instance.id.hex}/{get_random_name(filename)}"
    )
    return new_filename
