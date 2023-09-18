from dateutil import relativedelta
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .constants import ALLOWED_MAIL_PROVIDER
import re
from django.utils.translation import gettext_lazy as _


class UppercaseValidator(object):

    """The password must contain at least 1 uppercase letter, A-Z."""

    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise DjangoValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, A-Z.")


class SpecialCharValidator(object):

    """The password must contain at least 1 special character @#$%!^&*"""

    def validate(self, password, user=None):
        if not re.findall("[@#$%!^&*]", password):
            raise DjangoValidationError(
                _(
                    "The password must contain at least 1 special character: "
                    + "@#$%!^&*"
                ),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character: " + "@#$%!^&*"
        )


def verify_valid_mail(email):
    server = email.split("@")[-1]
    if server not in ALLOWED_MAIL_PROVIDER:
        raise ValidationError(
            f"Invalid mail {email}, It must be any of this providers {ALLOWED_MAIL_PROVIDER}"
        )
    return email


def verify_contact(contact):
    if len(contact) != 14 or "+234" not in contact:
        raise ValidationError(
            """
            You have to provide a 13 digit contact number and include country code.
              only support Nigeria for now e.g(+2348073838438 )"""
        )
    return contact


def validate_date_above(date):
    now = timezone.now().date()
    delta = relativedelta.relativedelta(now, date)
    years_diff = delta.years
    if years_diff < 18:
        raise ValidationError(
            f"Invalid {date}, You must be greater than 18 to be registered!!!"
        )
    return date


def validate_password_for_user(password, user=None):
    errors = dict()
    try:
        validate_password(password=password, user=user)
    except ValidationError as e:
        error_messages = ", ".join(list(e.messages))
        errors["password"] = error_messages
    except DjangoValidationError as e:
        error_messages = ", ".join(list(e.messages))
        errors["password"] = error_messages

    if errors:
        raise ValidationError(errors)


def true_validator(value):
    if not value:
        raise ValidationError("This field must be an even number.")
    return value


# class MinimumLengthValidator:
#     def __init__(self, min_length=8):
#         self.min_length = min_length

#     def validate(self, password, user=None):
#         if len(password) < self.min_length:
#             raise ValidationError(
#                 _("This password must contain at least %(min_length)d characters."),
#                 code='password_too_short',
#                 params={'min_length': self.min_length},
#             )

#     def get_help_text(self):
#         return _(
#             "Your password must contain at least %(min_length)d characters."
#             % {'min_length': self.min_length}
#         )
