from pathlib import Path
import shutil
import base64
import csv
import hashlib
import io
import itertools
import json
import logging
import math
import mimetypes
import operator
import os
import random
import re
import secrets
import string
import traceback
import urllib
import uuid
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import reduce
from io import BytesIO
from tempfile import SpooledTemporaryFile
from urllib.request import urlopen
from uuid import UUID
from typing import Any
import boto3
import jwt
import magic
import pandas as pd
import phonenumbers
import pytz
import requests
import six
from Crypto import Random
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework.exceptions import APIException
from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import get_default_password_validators
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.paginator import InvalidPage
from django.db.models import IntegerField, Q, Subquery
from django.http import QueryDict
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import datetime
from django.utils.timezone import datetime as dt
from django.contrib import admin
from django.utils.translation import gettext as _
from PIL import Image
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from storages.backends.s3boto3 import S3Boto3Storage
from rest_framework.throttling import UserRateThrottle
from user.choices import RoleType
from strings import (
    INVALID_FILE_EXTENSION_MESSAGE,
    ALLOWED_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS,
    LIMITED_ALLOWED_EXTENSIONS,
)


logger = logging.getLogger("__name__")


class CustomS3Boto3Storage(S3Boto3Storage):
    querystring_auth = True
    default_acl = None

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CustomS3Boto3Storage, self)._save_content(
            obj, content_autoclose, parameters
        )

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()


class StaticS3Boto3Storage(CustomS3Boto3Storage):
    if settings.ENV in ["production", "prod", "staging", "stag"]:
        default_acl = "public-read"
        querystring_auth = False
        bucket_name = settings.AWS_STATIC_STORAGE_BUCKET_NAME
    else:
        pass


class CustomException(Exception):
    pass


class CapitalLetterValidator(object):
    HELP_TEXT = "Password should contain at least one capital letter"

    def validate(self, password, user=None):
        if not any(str(x).isupper() for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


class NumericCharacterValidator(object):
    HELP_TEXT = "Password should contain at least one number"

    def validate(self, password, user=None):
        if not any(x in string.digits for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


class SpecialCharacterValidator(object):
    HELP_TEXT = "Password should contain at least one special character"

    def validate(self, password, user=None):
        if not any(x in string.punctuation for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


def custom_password_validator(password, user=None, password_validators=None):
    errors = []
    if " " in password:
        errors.append("Password cannot contain blank space")
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.extend(error.messages)

    if errors:
        if user:
            raise serializers.ValidationError(detail={"password": errors})
        else:
            raise serializers.ValidationError(detail=errors)


def validate_image(value):
    if hasattr(value, "content_type"):
        if value.content_type.split("/")[0] != "image":
            raise serializers.ValidationError(detail="Please upload a valid image file")
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise serializers.ValidationError(
            detail="File size should be less than 10 Megabytes"
        )


def get_image_from_b64(data):
    format, imgstr = data.split(";base64")
    random_name = "".join(random.choice(string.ascii_letters) for _ in range(9))
    filename = random_name + ".png"
    image = ContentFile(base64.b64decode(imgstr), name=filename)
    return image


def get_file_from_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Magic Browser"})
    input_file = io.BytesIO(urlopen(req).read())
    content_type = magic.from_buffer(input_file.getvalue(), mime=True)
    extension = mimetypes.guess_extension(content_type)
    temp_file = TemporaryUploadedFile(
        name=secrets.token_hex(10) + extension,
        content_type=content_type,
        size=input_file.__sizeof__(),
        charset=None,
    )
    temp_file.file.write(input_file.getvalue())
    temp_file.file.seek(0)
    return extension, temp_file


def get_dict_data(data):
    if isinstance(data, dict):
        return data
    else:
        return data.dict()


class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 100


def phonenumber_validator(value):
    try:
        z = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(z):
            raise ValidationError("Please enter a valid phone number")
    except Exception as e:
        if settings.ENV == "development":
            raise ValidationError(str(e))
        else:
            raise ValidationError(
                "Please enter a valid phone number with international code"
            )
    return phonenumbers.format_number(z, phonenumbers.PhoneNumberFormat.E164)


def create_otp(length):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def get_jwt_auth_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def random_file_name(extension, length):
    random_name = "".join(random.choice(string.ascii_letters) for _ in range(length))
    return random_name + timezone.localdate().strftime("%Y%m%d") + extension


class SQCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


def get_sms_client():
    sms_client = boto3.client("sns", region_name=settings.SNS_REGION)
    sms_client.set_sms_attributes(attributes={"DefaultSMSType": "Transactional"})
    return sms_client


def make_mutable(data):
    return setattr(data, "_mutable", True) if type(data) == QueryDict else None


def get_boolean(x):
    if type(x) == bool:
        return x
    if x:
        if x.lower() == "true" or x == 1 or x == "1" or x == "t":
            return True
        else:
            return False
    else:
        return False


def get_thumbnail_url(url):
    s3 = boto3.client("s3")
    thumbnail_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": "thumbnails/" + ".".join(url.split(".")[:-1] + ["png"]),
            "ResponseExpires": timezone.now() + timezone.timedelta(hours=23),
        },
    )
    return thumbnail_url


def is_valid_uuid(value):
    """
    Check if a given value is a valid UUID.

    Parameters:
        value (str): The value to check.

    Returns:
        bool: True if the value is a valid UUID, False otherwise.
    """
    import uuid

    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def random_password(length):
    key = ""
    for i in range(length):
        key += random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        )
    return key


def success_response(
    success=True,
    data=None,
    message=None,
    request=None,
    code="success",
    status_code=status.HTTP_200_OK,
):
    return Response(
        {"success": True, "data": data, "message": message, "code": code},
        status=status_code,
    )


def error_response(
    success=False,
    data=None,
    message=None,
    request=None,
    code="error",
    detail=None,
    status_code=status.HTTP_400_BAD_REQUEST,
):
    return Response(
        {
            "success": False,
            "data": data,
            "message": message,
            "code": code,
            "detail": detail,
        },
        status=status_code,
    )


class AESCipher(object):
    """This code snippet defines a class called AESCipher that provides methods for encrypting and
    decrypting data using the AES encryption algorithm. The __init__ method initializes the cipher
    with a given key. The encrypt method takes a raw string as input, pads it, generates an initialization
    vector (IV), creates a cipher object, and returns the encrypted data in base64-encoded format.
    The decrypt method takes an encrypted string, decodes it from base64, extracts the IV,
    creates a cipher object, decrypts the data, and returns the decrypted string.
    The _pad and _unpad methods are helper functions for padding and unpadding the data to
    ensure it is of the correct length for encryption."""

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]


def generate_email_and_password():
    """
    Generates a random email address and a strong password.

    Parameters:
    None

    Returns:
    email (str): The randomly generated email address.
    password (str): The randomly generated strong password.
    """
    domain = settings.EMAIL_DOMAIN
    # Generate a random name
    name_length = 8
    random_name = "".join(
        random.choice(string.ascii_lowercase) for _ in range(name_length)
    )

    # Generate the email
    email = f"{random_name}@{domain}"

    # Generate a strong password
    characters = string.ascii_letters + string.digits
    password_length = 12
    password = "".join(random.choice(characters) for _ in range(password_length))

    return email, password


def generate_unique_code(length):
    characters = string.ascii_letters.upper() + string.digits
    unique_code = "".join(random.choice(characters) for _ in range(length))

    return unique_code


def read_json_file(file_path: str) -> dict:
    json_data = {}
    with open(file_path) as country_file:
        json_data = json.load(country_file)
    return json_data


def generate_unique_code_using_crypto_module(length: int = 10) -> str:
    """generate unique code using django.utils.crypto"""
    code = get_random_string(
        length, allowed_chars=string.ascii_uppercase + string.digits
    ).upper()
    return code


def generate_unique_terminal_code_w_prefix(length: int = 10) -> str:
    """generate unique code started with ZC8 using django.utils.crypto"""
    return f"{settings.TERMINAL_CODE_START_WITH}{generate_unique_code_using_crypto_module()}"


def validate_file_extension(valid_extensions: list, value):
    # Get the file extension from the uploaded file
    ext = os.path.splitext(value.name)[1]

    # Check if the file extension is not in the list of valid extensions
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            INVALID_FILE_EXTENSION_MESSAGE,
            params={"allowed": ", ".join(valid_extensions)},
        )


def validate_document_extension(value):
    validate_file_extension(ALLOWED_EXTENSIONS.split(","), value)


def validate_consultation_recording_extension(value):
    validate_file_extension(ALLOWED_AUDIO_EXTENSIONS.split(","), value)


def validate_medical_document_extension(value):
    validate_file_extension(LIMITED_ALLOWED_EXTENSIONS.split(","), value)


def convert_datetime_str_to_datetime(date_str=None, time_str=None, format="%Y/%m/%d"):
    if date_str:
        return datetime.strptime(date_str, format)
    elif time_str:
        return datetime.strptime(time_str, "%H:%M")


def convert_datetime_into_utc(
    datetime_str=None,
    source_timezone="",
    format="%Y/%m/%d %H:%M:%S",
):
    """if none we return None"""
    # NOTE - for vendor's datetime format
    if datetime_str is not None:
        source_tz = pytz.timezone(source_timezone)
        datetime_component = datetime.strptime(datetime_str, format)
        localized_datetime = source_tz.localize(datetime_component)
        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        return utc_datetime


def check_is_decimal_and_convert_to_float(value):
    """This function if value is decimal then convert to float else return same value"""
    if isinstance(value, Decimal):
        return float(value)
    return value


def convert_payload_decimal_value_to_float(validated_data: dict) -> dict:
    validated_data = dict(
        validated_data
    )  # this ordered dict in order to change ,changing to dict

    for key, value in validated_data.items():
        checked_value = check_is_decimal_and_convert_to_float(value)
        validated_data[key] = checked_value

    return validated_data


def get_epoch_datetime():
    """This function return epoch datetime using datetime python library"""
    current_datetime = dt.now()
    current_timestamp = int(current_datetime.timestamp())
    return current_timestamp


def get_current_datetime():
    # This function return current datetime
    return dt.now(tz=pytz.UTC)


def save_data_into_csv(data: list) -> BytesIO:
    df = pd.DataFrame(data)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer


def get_host(request):
    return f"{'https' if request.is_secure() else 'http'}://{request.META['HTTP_HOST']}"


def convert_id_to_uuid(id: str) -> UUID:
    """this function convert id to UUID"""
    return UUID(id)


def read_csv_file_with_pandas(file_data):
    """
    Reads a CSV file from file_data using Pandas and returns a DataFrame.

    Args:
        file_data: The file data, usually from a Django file upload.

    Returns:
        A Pandas DataFrame representing the CSV data.
    """
    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(file_data, dtype=str)
        data = df.to_dict(orient="records")

        if len(df) > 200:
            raise ValidationError(_("Rows must be less than 200"))

        return data

    except Exception as e:
        # Handle any exceptions that may occur during reading the CSV file.
        # You can log the error or raise a specific exception as needed.
        raise e


def retry_function(func_list, max_retries=settings.MAX_RETRY_LIMIT):
    """
    Retries a list of functions until they all succeed or the maximum number of retries is reached.

    Args:
        func_list (list): A list of functions to be retried.
        max_retries (int): The maximum number of retries allowed.

    Raises:
        APIException: If any function fails.

    Returns:
        None
    """
    for func in func_list:
        retries = max_retries
        while retries:
            try:
                func()
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise e


def convert_utc_iso_into_datetime_obj(data):
    return timezone.datetime.fromisoformat(data[:19]).replace(tzinfo=timezone.utc)


def extract_first_last_name(full_name):
    if not full_name or not full_name.strip():
        return (
            "no",
            "name",
        )  # those who have no name we are saving the random no name string for them

    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    if len(name_parts) > 2:
        middle_name = " ".join(name_parts[1:-1])
        first_name += " " + middle_name
    return first_name, last_name


def get_instance_data(data, vendor_id):
    return next((item for item in data if item.vendor_id == vendor_id), None)


def get_instance_data_by_id(data, id):
    return next((item for item in data if item.id == id), None)


def unique_dicts(original_list):
    return [
        json.loads(item)
        for item in {json.dumps(d, sort_keys=True) for d in original_list}
    ]


def check_unique_combination(unique_data):
    combination_set = set()

    for item in unique_data:
        vehicle_code = item["vehicle_code"]
        driver_code = item["driver_code"]
        combination = (vehicle_code, driver_code)

        if combination in combination_set:
            return False

        combination_set.add(combination)

    return True


def get_codes_uuid(values):
    uuid_list = []
    non_uuid_list = []

    for value in values:
        try:
            uuid.UUID(value)
            uuid_list.append(value)
        except ValueError:
            non_uuid_list.append(value)

    uuid_list = list(set(uuid_list))
    non_uuid_list = list(set(non_uuid_list))

    return uuid_list, non_uuid_list


def is_credit_limit_80_percent_used(available_limit, credit_limit):
    """
    Check if the credit limit is 80% used.

    Args:
    - available_limit (Decimal): The available credit limit.
    - credit_limit (Decimal): The total credit limit.

    Returns:
    - bool: True if the credit limit is 80% used, False otherwise.
    """
    threshold_percentage = 80
    threshold_balance = (threshold_percentage / 100) * float(credit_limit)

    return available_limit <= Decimal(threshold_balance)


def is_html(string):
    html_pattern = re.compile(r"<.*?>")
    return bool(html_pattern.search(string))


def is_xml_present(response):
    # Check if the "XML" key is present in the response JSON
    if "XML" in response:
        xml_string = response["data"]["data"]["XML"]
        xml_pattern = re.compile(r"<.*?>")
        return bool(xml_pattern.search(xml_string))
    return False


def convert_to_json_compatible(data):
    if isinstance(data, UUID):
        return str(data)
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {key: convert_to_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    else:
        return data  # Return as is for other types


def decode_binary_str_to_json(binary_str: bytes) -> json:
    """It takes binary string eg: b'["data","hi"]'"""
    decoded_data = []
    try:
        decoded_str = binary_str.decode("utf-8", errors="replace")
        decoded_data = json.loads(decoded_str)
    except Exception as e:
        pass  # unable to decode

    return decoded_data


def decode_jwt_token(token: str, key=str, algorithms=["HS256"]):
    """
    :param token: jwt token
    :return:
    """

    return jwt.decode(jwt=token, key=key, algorithms=algorithms, verify=False)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def check_valid_number(number: str | Decimal) -> Decimal:
    convert_number = Decimal("0")
    is_valid_number = False
    try:
        convert_number = Decimal(number)
        is_valid_number = True

    except ValueError:
        pass
    finally:
        return convert_number, is_valid_number


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return str(o)
        return super(CustomJsonEncoder, self).default(o)


class CustomResponse:
    def __init__(self, response):
        self.response = response.json()["response"]
        self.text = response.text
        self.status_code = response.status_code
        self.headers = response.headers
        self.json_data = (
            json.loads(response.text)
            if "application/json" in response.headers.get("content-type", "").lower()
            else None
        )

    @property
    def message(self):
        # Customize this method based on the response structure of the API
        # For example, you might want to extract a specific message from the JSON response
        return self.json_data.get("message") if self.json_data else None

    @property
    def success(self):
        # Check if the response indicates success based on your API's structure
        return self.json_data.get("response") == "success" if self.json_data else False

    @property
    def error_message(self):
        # Extract error message from the JSON response
        return (
            self.json_data.get("message", {}).get("message") if self.json_data else None
        )

    @property
    def error_detail(self):
        # Extract error detail from the JSON response
        return (
            self.json_data.get("message", {}).get("messageDetail")
            if self.json_data
            else None
        )

    @property
    def xml_error(self):
        # Extract XML error from the JSON response
        return self.json_data.get("xmlerror") if self.json_data else None

    @property
    def uuid(self):
        # Extract UUID from the JSON response
        return self.json_data.get("uuid") if self.json_data else None


def convert_enum_class_to_dict(enum_class: Enum) -> dict:
    """It accepts Enum object and it return dict"""
    return dict(map(lambda item: (item.name, item.value), enum_class))


def search_key_on_dict(dict_value: dict, key_to_be_found) -> str | int:
    """This function takes key and search in all the dict,if found then it will return"""
    value_found = ""
    for key, value in dict_value.items():
        # value is in tuple
        if key_to_be_found == value[0]:
            value_found = value[1]
            break

    return value_found


def convert_datetime_to_str(datetime_obj, format="%m/%d/%Y, %H:%M:%S") -> str:
    return datetime_obj.strftime(format)


def is_current_user_mqg_user(logged_in_user_roles: list, mqg_roles: list) -> bool:
    return any([role in mqg_roles for role in logged_in_user_roles])


def extract_id_as_str_from_instances(
    instances_list: list,
    empty_message: str,
) -> list:
    """
    Validate instances list and convert their IDs to strings for Celery.

    Args:
        instances (list): List of database model instances.
        empty_message (str): Message to raise if instances list is empty.

    Returns:
        list: List of IDs as strings.

    Raises:
        ValidationError: If instances list is empty.
    """
    if not instances_list:
        raise APIException(empty_message)

    return [str(instance.id) for instance in instances_list]


def calculate_hour_difference_between_two_datetime(current_datetime, previous_datetime):
    """on calculating difference,it returns result in seconds"""
    return (current_datetime - previous_datetime).total_seconds() // 3600


def generate_ref_id_for_report():
    """this function return RefId in Caps"""
    return generate_unique_code(8)


class EntityException(APIException):
    def __init__(self, entity_id, entity_type, detail=None, code=None):
        self.default_code = status.HTTP_400_BAD_REQUEST
        self.default_detail = f"To execute the request, you must have {entity_type} entity access with entity ID {entity_id}."
        super().__init__(detail, code)


def get_yes_no_from_value_presence(value: Any) -> str:
    return "Yes" if value else "No"


class LoginThrottleRate(UserRateThrottle):
    rate = settings.LOGIN_THROTTLE_RATE


def get_full_file_path(file_path: str):
    return Path(f"{settings.MEDIA_ROOT}\{file_path}")


def delete_media(file_directory: str) -> bool:
    try:
        shutil.rmtree(
            os.path.normpath(
                os.path.join(settings.MEDIA_ROOT, str(Path(file_directory).parent))
            )
        )
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False
    return True
