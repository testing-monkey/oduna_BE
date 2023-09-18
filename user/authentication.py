from datetime import timedelta
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from core.utils import ExpiringActivationTokenGenerator
from user.models import PasswordResetWhitelist, User
from django.db.models import Q


class TokenAuthentication(BaseTokenAuth):
    keyword = "Token"


def check_user_lock(user):
    now = timezone.now()
    password_failure_count = user.password_failure_count
    lock_period = user.lock_period
    reason_for_lock = user.reason_for_lock
    if lock_period and lock_period > now:
        raise ValidationError(f"{reason_for_lock}. You must have exceeded lock period")


def check_password_health(user):
    password_update_grace_period_in_days = settings.PASSWORD_UPDATE_GRACE_PERIOD_IN_DAYS
    last_update_plus_grace_time = user.last_password_update + timedelta(
        days=password_update_grace_period_in_days
    )
    if timezone.now() > last_update_plus_grace_time:
        reset_token = ExpiringActivationTokenGenerator().generate_token(text=user.email)
        PasswordResetWhitelist.objects.create(
            email=user.email, token=reset_token.decode("utf-8")
        )
        raise ValidationError(
            {
                "message": "You must change password every %s days"
                % password_update_grace_period_in_days,
                "code": "01",
                "reset_token": reset_token,
            }
        )


class CustomAuthBackend(ModelBackend):
    def authenticate(
        self, *request, username=None, email=None, password=None, **kwargs
    ):
        # user = super().authenticate(request, username, password, **kwargs)
        users = User.objects.filter(
            email=email
        )
        if not users.exists():
            return
        user = (
            users.first()
            if users.first().check_password(password)
            else None
            # users.first().update_user_password_count(None)
        )
        if user:
            # check_user_lock(user)
            check_password_health(user)
            user.refresh_login_token()
        else:
            pass
        return user


def user_authentication_rule(user):
    if not user:
        raise AuthenticationFailed(
            "Credential(Username or Password) are incorrect, please contact support"
        )
    if not user.is_active:
        raise AuthenticationFailed("User is not active, please contact support")
    if not user.is_verified:
        raise AuthenticationFailed("User is not yet verified")
    if user.is_deleted:
        raise AuthenticationFailed("User is deleted, please contact support")
    return True
