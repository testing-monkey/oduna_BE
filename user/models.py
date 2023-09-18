import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from core.models import CoreModel, DeleteModelMixin, GeographicInfoModel
from core.utils import ExpiringActivationTokenGenerator, encode_data, send_mail
from user.choices import Gender, PasswordChangeStatus, UserType
from user.validators import validate_password_for_user

from .literals import (
    PASSWORD_RESET_RECORD_NOT_FOUND,
    PROFILE_PHOTO_DIRECTORY,
    RESET_PASSWORD_WITH_SIMILAR_PASSWORD,
)
from .managers import UserCustomManager

# logger = logging.get# logger("main")


# Create your models here.
class PasswordResetWhitelist(DeleteModelMixin, CoreModel):
    email = models.EmailField()
    token = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=PasswordChangeStatus.choices,
        default=PasswordChangeStatus.PENDING,
    )

    class Meta:
        unique_together = ("email", "token")


class User(AbstractUser, DeleteModelMixin, CoreModel, GeographicInfoModel):
    email = models.EmailField(_("email"), unique=True)
    contact_no = models.CharField(
        _("contact number"), max_length=50, blank=True, null=True
    )
    profession = models.CharField(
        _("professsion"), max_length=50, blank=True, null=True
    )
    position_held = models.CharField(
        _("professsion"), max_length=50, blank=True, null=True
    )
    user_type = models.CharField(
        _("user type"),
        max_length=20,
        choices=UserType.choices,
        default=UserType.MEMBER,
    )
    
    is_verified = models.BooleanField(_("is verified"), default=False)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    gender = models.CharField(
        _("gender"),
        max_length=30,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY,
    )
    user_login_token = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(
        upload_to=PROFILE_PHOTO_DIRECTORY,
        default="default_profile_picture.png",
        blank=True,
        null=True,
    )
    username = None
    objects = UserCustomManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return f"{self.email} ({self.user_type}) {self.full_name}"

    def __repr__(self) -> str:
        return self.email

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"


    def refresh_login_token(self, save=True):
        self.user_login_token = f"{self.email}-{uuid.uuid4().hex}"
        if save:
            self.save()

    @classmethod
    def from_validated_data(cls, validated_data: dict):
        validated_data["password"] = make_password(validated_data.pop("password"))
        user = super().from_validated_data(validated_data)
        return user

    @classmethod
    def get_hidden_fields(cls):
        return super().get_hidden_fields() + [
            "date_joined",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_verified",
            "is_active",
            "user_login_token",
            "user_permissions",
            "groups",
            "created_at",
        ]

    @classmethod
    def read_only_fields(cls, extra_fields=("email", "email")):
        return (
            "date_joined",
            "is_verified",
           
        ) + (extra_fields)

    @classmethod
    def write_only_fields(cls):
        return [
            "password",
        ]
    
    @property
    def has_completed_profile(self):
        required_fields = ["state", "first_name", "last_name"]
        
        return True, None

    def send_password_reset_mail(self) -> None:
        template = "emails/password_reset.html"
        reset_token = ExpiringActivationTokenGenerator().generate_token(text=self.email)
        try:
            _ = PasswordResetWhitelist.objects.create(
                email=self.email, token=reset_token.decode("utf-8")
            )
        except IntegrityError:
            raise ValidationError("Password reset mail is already sent.")

        # account/recovery/reset/:id/
        link = (
            "/".join(
                [
                    settings.FRONTEND_URL,
                    "account",
                    "recovery",
                    "reset",
                ]
            )
            + f"?token={reset_token.decode('utf-8')}"
        )
        send_mail(
            to_email=self.email,
            subject="Password Reset",
            template_name=template,
            input_context={
                "name": self.full_name,
                "link": link,
                "host_url": Site.objects.get_current().domain,
            },
        )

    def initiate_notification_mail(self, to_email) -> None:
        template = "emails/initiate_notification.html"
        data = {
            "email": self.email,
            "email": to_email,
            "user_id": str(self.id),
        }
        token = encode_data(data=data)
        link = (
            "/".join(
                [
                    settings.FRONTEND_URL,
                    "complete",
                    "email",
                ]
            )
            + f"?token={token}"
        )
        send_mail(
            to_email=to_email,
            subject="Initiate Notification Email",
            template_name=template,
            input_context={
                "name": self.full_name,
                "token": token,
                "link": link,
                "host_url": Site.objects.get_current().domain,
            },
        )

    @classmethod
    def generate_full_name(cls, first_name: str, last_name: str) -> str:
        full_name = f"{first_name} {last_name}"
        return full_name

    @classmethod
    def verify_password_reset(cls, token: str, password: str) -> None:
        user = None
        whitelist_token = None
        try:
            whitelist_token = PasswordResetWhitelist.objects.get(token=token)
        except PasswordResetWhitelist.DoesNotExist:
            raise ValidationError(PASSWORD_RESET_RECORD_NOT_FOUND)
        email = ExpiringActivationTokenGenerator().get_token_value(token)
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            raise ValidationError(f"Invalid token. {user.email} not found")
        validate_password_for_user(password=password, user=user)
        if user.check_password(password):
            raise ValidationError(RESET_PASSWORD_WITH_SIMILAR_PASSWORD)
        user.set_password(password)
        user.refresh_login_token(save=False)
        user.last_password_update = timezone.now()
        user.save()
        whitelist_token.delete()

    

    def send_email_verification_mail(self):
        template = "emails/registration.html"

        confirmation_token = ExpiringActivationTokenGenerator().generate_token(
            text=self.email
        )

        link = (
            "/".join(
                [
                    settings.FRONTEND_URL,
                    "email-verification",
                ]
            )
            + f"?token={confirmation_token.decode('utf-8')}"
        )
        send_mail(
            to_email=self.email,
            subject="Verify User Account",
            template_name=template,
            input_context={
                "name": self.full_name,
                "link": link,
                "host_url": Site.objects.get_current().domain,
            },
        )



class AccessLog(CoreModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_logs")
    meta = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=255)
    user_agent = models.TextField()
    # meta = models.JSONField(null=True, blank=True)
    # location = models.JSONField()
    location = models.TextField()
    user_login_token = models.CharField(max_length=100)
    status_code = models.IntegerField()
    device_ip = models.CharField(max_length=64)
    request_id = models.CharField(max_length=50)
