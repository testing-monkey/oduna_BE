import logging

from django.conf import settings
from rest_framework.exceptions import (
    ValidationError,
    ErrorDetail,
    APIException,
    PermissionDenied,
)
from rest_framework.views import exception_handler

# # logger = logging.get# logger("main")


def recursive_error_message_creator(error_dict):
    """
    Recursively creates a string from a dictionary of errors.
    """
    if isinstance(error_dict, list):
        return " ".join([error.__str__() for error in error_dict])
    message_list = ""
    for k, v in error_dict.items():
        if isinstance(v, str):
            message_list += v
        else:
            if message_list != "":
                message_list += " "
            message_list += f"{k}: {recursive_error_message_creator(v)}"
    return message_list


def custom_exception_handler(exception, context):
    response = exception_handler(exception, context)
    message = "Response is none"
    if response is not None:
        data = response.data
        message_list = []
        if isinstance(data, dict):
            message_list.append(recursive_error_message_creator(data))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    message_list.append(item)
                elif isinstance(item, ErrorDetail):
                    message_list.append(item.__str__())

        error_message = " ".join(message_list)
        error_message = error_message.replace("non_field_errors: ", "")
        custom_response = {
            "status_code": response.status_code,
            "result": None,
            "error": error_message,
        }
        response.data = custom_response
        message = f"data: {response.data}"
    # # logger.info(
    #     message
    # ) if settings.DEBUG is False and settings.ENVIRONMENT == "PRODUCTION" else None
    return response


class NotImplementedException(ValidationError):
    def __init__(self, detail="Invalid Data", code="InvalidData", data=None):
        super(NotImplementedException, self).__init__(detail, code)
        message = f"Invalid data: {data}"
        # # logger.info(message)


class IncorrectDataInRequest(ValidationError):
    def __init__(self, detail="Feature not implemented", code="NotImplemented"):
        super(NotImplementedException, self).__init__(detail, code)


class ApiRequestException(ValidationError):
    def __init__(
        self,
        url=None,
        method=None,
        headers=None,
        body=None,
        response=None,
        status_code=None,
        detail="Gateway Error",
        code="Gateway Error",
    ):
        super(ApiRequestException, self).__init__(detail, code)
        message = f"API_EXCEPTION  url:{url}, method:{method}, body: {body},\
             response: {response}, status_code: {status_code}"
        # # logger.info(message)


class CustomPermissionDenied(PermissionDenied):
    def __init__(
        self,
        detail="You dont have the required permissions",
        code="Permiision Error",
    ):
        super(CustomPermissionDenied, self).__init__(detail, code)
