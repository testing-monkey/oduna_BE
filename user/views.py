import uuid

 # add this
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView




from core.utils import ExpiringActivationTokenGenerator, decode_data
from user.choices import PasswordChangeStatus
from user.literals import (
 
    USER_LOGOUT_SUCCESSFUL,
)

from .models import PasswordResetWhitelist, User
from .serializers import (
    ChangePasswordSerializer,
    ConfirmEmailSerializer,
    ForgotPasswordSerializer,
    MyTokenObtainPairSerializer,
    NotificationSerializer,
    PasswordResetSerializer,
    ResendVerificationMailSerializer,
    TokenSerializer,
    UserPublicProfileSerializer,
)
from .tasks import send_email_verification_mail_async

# from .tasks import send_to_token_async

# logger = logging.get# logger("main")

# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    """
    This API is used to login with email and password
    """

    schema_dict = {
        "summary": "Login with email and password",
    }
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        response = super().post(request, *args, **kwargs)
        return response


class InitiatePasswordResetView(APIView):
    """
    This API is used to initial a password reset from a user who has forgotten their password.
    It will always return 200 ok
    """

    schema_dict = {
        "summary": "Initiatate a Password Reset",
    }

    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data["user"]
        data = {"message": "Email Has Been sent to the email provided"}
        if user is None:
            return Response(status=status.HTTP_200_OK, data=data)
        user.send_password_reset_mail()
        return Response(status=status.HTTP_200_OK, data=data)


class LogoutView(APIView):
    """
    This API is used to logout all users from the server.
    """

    schema_dict = {"summary": "Logout All User Accounts"}
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.refresh_login_token()
        return Response(
            status=status.HTTP_200_OK, data={"message": USER_LOGOUT_SUCCESSFUL}
        )


class CompletePasswordResetView(GenericAPIView):
    """
    This API is used to complete a forget password reset,
    You have to pass the token to complete the reset
    """

    schema_dict = {
        "summary": "Complete a Password Reset",
    }
    permission_classes = [AllowAny]
    http_method_names = ["post", "options"]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        # Extracting data from request and validating it
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        User.verify_password_reset(**validated_data)
        return Response(
            status=status.HTTP_200_OK, data={"message": "Password Reset Completed"}
        )


class InitiateNotificationEmailView(GenericAPIView):
    """
    This API is used to complete a forget password reset,
    You have to pass the token to complete the reset
    """

    schema_dict = {
        "summary": "Complete a Password Reset",
    }
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "options"]
    serializer_class = NotificationSerializer

    def post(self, request):
        # Extracting data from request and validating it
        user = request.user
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = validated_data["email"]

        user.initiate_notification_mail(email)
        return Response(status=status.HTTP_200_OK, data={"message": "Check your email"})


class CompleteNotificationEmailView(GenericAPIView):
    """
    This API is used to complete a forget password reset,
    You have to pass the token to complete the reset
    """

    schema_dict = {
        "summary": "Complete a Password Reset",
    }
    permission_classes = []
    http_method_names = ["post", "options"]
    serializer_class = TokenSerializer

    def post(self, request):
        # Extracting data from request and validating it
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        token = data.get("token")
        token_data = decode_data(token)
        user_id = token_data.get("user_id")
        email = token_data.get("email")
        user = User.objects.get(id=user_id)
        user.email = email
        user.save()
        return Response(
            status=status.HTTP_200_OK, data={"message": "Notification Email Completed"}
        )


class UserProfileView(RetrieveAPIView, UpdateAPIView):
    """
    This API is used to get the user's profile details
    """

    schema_dict = {
        "summary": "Get the profile of the user",
    }
    serializer_class = UserPublicProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj


class ChangePasswordView(UpdateAPIView):
    """
    This API is used to change user's password.
    It is used when a user remembers the old password and wants to change
    to a new one. Use the forget password API to reset
    """

    schema_dict = {
        "summary": "Change User Password ",
    }
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = request.data["new_password"]
        self.object.set_password(password)
        self.object.last_password_update = timezone.now()
        self.object.save()
        _id = uuid.uuid4()
        change_password_keyword = PasswordChangeStatus.CHANGE_PASSWORD
        token = f"{change_password_keyword}__{_id}"
        PasswordResetWhitelist.objects.create(
            email=self.object.email, status=change_password_keyword, token=token
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Password changed"})


class ConfirmEmailView(GenericAPIView):
    """
    POST - Confirm verification email
    """

    schema_dict = {
        "summary": "Confirm Verification Mail",
        # 'tags': ['appointment_booking', "1"]
    }
    permission_classes = [AllowAny]
    serializer_class = ConfirmEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")
        decoded_data = ExpiringActivationTokenGenerator().get_token_value(token)
        email = decoded_data
        user = get_object_or_404(User, email=email)
        user.is_verified = True
        user.is_active = True
        user.active = True
        user.save()
        return Response(
            status=status.HTTP_200_OK, data={"message": "Email Verification successful"}
        )


class ResendVerificationMailView(GenericAPIView):
    """
    POST - Resend verification email
    """

    schema_dict = {
        "summary": "Redend Verification Mail",
        # 'tags': ['appointment_booking', "1"]
    }
    serializer_class = ResendVerificationMailSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        users = User.objects.filter(email=email, is_verified=False)
        if users.exists():
            user = users.first()
            send_email_verification_mail_async(user_id=user.id)
        message = "Check Your Email For Verification"
        data = {"message": message}
        return Response(status=status.HTTP_200_OK, data=data)
