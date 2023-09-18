import base64

from core.utils import send_mass_mail


def send_newsletter(emails, subject, message, file=None):
    byte_data = base64.b64decode(file.encode(encoding="utf-8")) if file else None
    send_mass_mail(
        subject=subject,
        to_email=emails,
        message=message,
        file=byte_data,
    )
