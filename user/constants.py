from django.conf import settings


ALLOWED_MAIL_PROVIDER = ["gmail.com", "yahoo.com", "outlook.com"]

ALLOWED_MAIL_PROVIDER = (
    ALLOWED_MAIL_PROVIDER
    if settings.ENVIRONMENT == "PRODUCTION"
    else ALLOWED_MAIL_PROVIDER
    + [
        "mailinator.com",
        "mailinator.net",
    ]
)
