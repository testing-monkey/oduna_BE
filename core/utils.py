from datetime import datetime, timedelta
import logging
from random import randint
from typing import  Dict
import jwt

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from rest_framework.exceptions import ValidationError

GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/"


logger = logging.getLogger("main")



def get_date_object_from_age(age):
    now = timezone.now()
    fifty_years_from_now = timedelta(days=age * 365)
    years_ago = (now - fifty_years_from_now).date()
    return years_ago


def get_date_range_object_from_age(age_from, age_to):
    now = timezone.now()
    from_now = timedelta(days=age_from * 365)
    from_now_date = (now - from_now).date()
    to_now = timedelta(days=age_to * 365)
    to_now_date = (now - to_now).date()
    return from_now_date, to_now_date
def send_mass_mail(
    subject,
    to_email,
    message,
    file=None,
    is_info_mail=True,
):
    """
    Send Activation Email To User
    """
    # base_url = input_context.get("host_url", Site.objects.get_current().domain)
    try:
        # render email text
        email_html_message = message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=email_html_message,
            from_email=settings.INFO_EMAIL if is_info_mail else settings.SUPPORT_EMAIL,
            to=to_email,
        )
        msg.attach_alternative(email_html_message, "text/html")
        if file is not None:
            msg.attach("attached_file.png", file, "image/png")
        msg.send()
    except Exception as e:
        logger.error(f"{str(e)} ==> Failed to send email to {to_email}")


def send_mail(
    subject,
    to_email,
    input_context,
    template_name,
    file=None,
    cc_list=(),
    bcc_list=(),
    is_info_mail=True,
):
    """
    Send Activation Email To User
    """
    # base_url = input_context.get("host_url", Site.objects.get_current().domain)

    context = {
        "site": "ODUNA",
        "MEDIA_URL": settings.STATIC_URL[:-1],
        **input_context,
    }

    # render email text
    email_html_message = render_to_string(template_name, context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=email_html_message,
        from_email=settings.INFO_EMAIL if is_info_mail else settings.SUPPORT_EMAIL,
        to=[to_email],
        bcc=bcc_list,
        cc=cc_list,
    )
    msg.attach_alternative(email_html_message, "text/html")
    if file is not None:
        msg.attach("attached_file.png", file, "image/png")
    msg.send()


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def date_now_plus(days=365):
    mydate = timezone.now() + timedelta(days=days)
    return mydate
 

class ExpiringActivationTokenGenerator:
    def __init__(self):
        self.FERNET_KEYS = settings.FERNET_KEYS
        self.fernet = MultiFernet([Fernet(key) for key in self.FERNET_KEYS])
        self.DATE_FORMAT = "%Y-%m-%d %H-%M-%S"
        self.EXPIRATION_DAYS = 1

    def _get_time(self):
        """Returns a string with the current UTC time"""
        return datetime.utcnow().strftime(self.DATE_FORMAT)

    def _parse_time(self, d):
        """Parses a string produced by _get_time and returns a datetime object"""
        return datetime.strptime(d, self.DATE_FORMAT)

    def generate_token(self, text):
        """Generates an encrypted token"""
        full_text = text + "|" + self._get_time()
        string_to_byte = bytes(full_text, encoding="utf-8")
        token = self.fernet.encrypt(string_to_byte)
        return token

    def get_token_value(self, token):
        """Gets a value from an encrypted token.
        Returns None if the token is invalid or has expired.
        """
        try:
            converted_token_to_bytes = bytes(token, encoding="utf-8")
            value_in_bytes = self.fernet.decrypt(converted_token_to_bytes)
            # value_in_bytes = self.fernet.rotate(value_in_bytes)
            value = value_in_bytes.decode("utf-8")
            separator_pos = value.rfind("|")

            text = value[:separator_pos]
            token_time = self._parse_time(value[separator_pos + 1 :])

            if token_time + timedelta(self.EXPIRATION_DAYS) < datetime.utcnow():
                raise InvalidToken("Token expired.")
        except InvalidToken as e:
            raise ValidationError(f"Invalid token. {e}")
        return text


def encode_data(data: Dict, expiration_in_minutes: int = 30):
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(
        minutes=expiration_in_minutes
    )
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")


def decode_data(token):
    try:
        data = jwt.decode(
            token,
            settings.SECRET_KEY,
            leeway=timedelta(minutes=2),
            algorithms=["HS256"],
        )
        return data
    except jwt.ExpiredSignatureError:
        raise ValidationError("Token is expired")

