from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    ChangePasswordView,
    CompleteNotificationEmailView,
    CompletePasswordResetView,
    ConfirmEmailView,
    InitiateNotificationEmailView,
    InitiatePasswordResetView,
    MyTokenObtainPairView,
    ResendVerificationMailView,
    UserProfileView,
)

# from .views import MyTokenObtainPairView

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "resend_verification_mail/",
        ResendVerificationMailView.as_view(),
        name="resend_verification_mail",
    ),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path(
        "initiate_password_reset/",
        InitiatePasswordResetView.as_view(),
        name="initiate_password_reset",
    ),
    path(
        "complete-password-reset/",
        CompletePasswordResetView.as_view(),
        name="complete_password_reset",
    ),
    path(
        "initiate-notification-email-add/",
        InitiateNotificationEmailView.as_view(),
        name="initiate_email_reset",
    ),
    path(
        "complete-email-add/",
        CompleteNotificationEmailView.as_view(),
        name="complete_email_reset",
    ),
    path("confirm_email/", ConfirmEmailView.as_view(), name="confirm_email"),
  
]
