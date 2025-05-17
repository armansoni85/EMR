from rest_framework.exceptions import APIException

from django.core.exceptions import PermissionDenied
from django.core import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status, serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework_simplejwt.backends import TokenBackendError

# from common.middleware import get_request
from base.utils import is_valid_uuid, EntityException
from django.apps import apps
import re, traceback
from django.http import Http404
import logging
from strings import *
from response_codes import *
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exception, context):
    logger.exception(
        {
            "ref": "Exception caught in common exception handler",
            "exception": str(exception),
            "traceback": traceback.format_exc(),
        }
    )

    response = {}
    headers = {}
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    for i in apps.get_models():
        if isinstance(exception, i.DoesNotExist):
            message = MATCHING_ERROR_NOT_FOUND_MESSAGE
            model_name = re.sub(r"([a-z])([A-Z])", r"\1 \2", i.__name__).strip()
            if model_name:
                message += f" for {model_name}"
            response["message"] = message
            response["code"] = NOT_FOUND
            response["status"] = False
            status_code = status.HTTP_404_NOT_FOUND

    if isinstance(exception, IntegrityError):
        message = INVALID_REQUEST
        detail = str(exception.args[0])
        response["success"] = False
        response["message"] = message
        response["detail"] = detail
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    elif isinstance(exception, TokenBackendError):
        response["message"] = VALIDATION_ERROR_MESSAGE
        response["success"] = False
        response["errors"] = exception.args[0]
        status_code = status.HTTP_401_UNAUTHORIZED

    elif isinstance(exception, ValueError):
        response["message"] = VALIDATION_ERROR_MESSAGE
        response["success"] = False
        response["errors"] = exception.args[0]
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exception, ValidationError):
        response["message"] = VALIDATION_ERROR_MESSAGE
        response["success"] = False
        response["errors"] = exception
        response["code"] = UNPROCESSED_ENTITY
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    elif isinstance(exception, serializers.ValidationError):
        message = CORRECT_BELOW_ERRORS
        detail = exception.__dict__
        response = {}
        response["message"] = message
        response["detail"] = detail["detail"]
        response["success"] = False
        response["code"] = UNPROCESSED_ENTITY
        status_code = exception.status_code

    elif isinstance(exception, Http404):
        response["message"] = RESOURCE_NOT_FOUND_MESSAGE
        response["code"] = NOT_FOUND
        response["status"] = False
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exception, PermissionDenied):
        response["message"] = DO_NOT_HAVE_PERMISSION_MESSAGE
        response["success"] = False
        response["code"] = PERMISSION_DENIED
        status_code = status.HTTP_403_FORBIDDEN

    elif isinstance(exception, APIException):
        if getattr(exception, "auth_header", None):
            headers["WWW-Authenticate"] = exception.auth_header

        if getattr(exception, "wait", None):
            headers["Retry-After"] = "%d" % exception.wait

        data = exception.get_full_details()

        message = ""
        code = ""

        if "detail" in data:
            if "code" in data["detail"]:
                code = data["detail"]["code"]
            if "message" in data["detail"]:
                message = data["detail"]["message"]

        elif "code" in data:
            code = data["code"]
            if "message" in data:
                message = data["message"]

        if len(message) == 0:
            # request = get_request()
            # if request and request.session:
            #     if 'code' in request.session:
            #         if isinstance(data, dict):
            #             code = request.session['code']
            #         del request.session['code']

            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(k, str) and isinstance(v, list):
                        v = "%s" % (v[0] if not "message" in v[0] else v[0]["message"])
                    elif isinstance(k, str) and isinstance(v, str):
                        response.setdefault("data", {})[k] = v

            if len(data) > 1:
                message = APPLICATION_ERROR_MESSAGE
            else:
                key = list(data.keys())[0]
                if key == "non_field_errors":
                    key = "error"
                message = response["data"][key]

        response["message"] = message
        response["code"] = code
        response["success"] = False

        # response['data']['code'] = code
        # if "data" in response:
        #     del response["data"]

        if exception.get_codes() in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
        ]:
            status_code = exception.get_codes()
        elif code == PARSE_ERROR:  # it was code == 'parse_error'
            response["message"] = PARSE_ERROR_MESSAGE
        elif code == PASSWORD_CHANGE_NEEDED:
            status_code = status.HTTP_400_BAD_REQUEST

        elif (
            code != NOT_AUTHENTICATED
            and code != TOKEN_NOT_VALID
            and code != TOKEN_BLACK_LISTED
        ):
            logger.exception({"code": code, "message": str(message)})
            status_code = exception.status_code
        else:
            status_code = status.HTTP_401_UNAUTHORIZED
    if not response:
        response["message"] = SERVER_ERROR_MESSAGE
        response["success"] = False
        response["detail"] = None

    return Response(response, status=status_code, headers=headers)


def handler_exception_general(name, e):
    """
    Handle a general exception.

    Args:
        name (str): The logger name.
        e (Exception): The exception.

    Returns:
        tuple: A tuple containing the response message (str), a dictionary with the error code (str), and the response status (int).
    """
    logger.exception(e)

    if isinstance(e, EntityException):
        response_status = e.get_codes()
        response_message = e.default_detail
        response_data = {"code": "entity_access_error"}
    elif isinstance(e, APIException):
        response_status = status.HTTP_400_BAD_REQUEST
        response_message = API_ERROR_MESSAGE
        response_data = {"code": API_ERROR_CODE, "detail": e.detail}
    elif isinstance(e, KeyError):
        response_status = status.HTTP_400_BAD_REQUEST
        response_message = CORRECT_BELOW_ERRORS
        response_data = {
            "code": FIELD_REQUIRED,
            "detail": {e.args[0]: ["This field is required"]},
        }
    else:
        response_message = APPLICATION_ERROR_MESSAGE
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = {"code": GENERAL_ERROR_CODE}

    return response_message, response_data, response_status


def handler_exception_404(name, lookup_field, pk, e):
    """
    Handles exceptions for a 404 error.

    Args:
        name (str): The name of the logger.
        lookup_field (str): The lookup field.
        pk (str): The primary key value.
        e (Exception): The exception object.

    Returns:
        tuple: A tuple containing the response message, a dictionary with the code, and the response status.

    Raises:
        None
    """
    if lookup_field == "unique_id" and not is_valid_uuid(pk):
        response_message = "El valor {} no es valido".format(pk)
        response_status = status.HTTP_404_NOT_FOUND
    else:
        logger.exception(e)
        response_message = RECORD_NOT_FOUND_MESSAGE
        response_status = status.HTTP_404_NOT_FOUND
    return response_message, {"code": NOT_FOUND}, response_status


def get_response_data_errors(data, version="v1"):
    """
    Generate the response data errors based on the input data and version.

    Parameters:
    - data (dict): The input data to generate the response data errors.
    - version (str): The version of the API. Default is 'v1'.

    Returns:
    - tuple: A tuple containing the response data errors and the error message.
      - If version is 'v1', returns (data, message).
      - If version is not 'v1', returns (message, data, 422).
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, list):
                m = "" if k == NON_FIELD_ERRORS else f"{k.capitalize()}: "
                for v_i in v:
                    if len(m) == 0:
                        m += "%s " % v_i
                    else:
                        m += "%s " % v_i
                v = m
            if isinstance(k, str) and isinstance(v, str):
                if isinstance(data, dict):
                    data[k] = v
                else:
                    data[k] += "%s: %s" % (k, v)
    if len(data) > 0:
        key = list(data.keys())[0]
        message = data[key]
    else:
        message = ERROR_IN_THE_REQUEST
    if version == "v1":
        return data, message
    else:
        return message, data, status.HTTP_422_UNPROCESSABLE_ENTITY
