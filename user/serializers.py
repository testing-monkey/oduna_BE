from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from user.choices import Gender
from user.utils import  login_data

from .literals import (
    INCORRECT_OLD_PASSWORD,
    INVALID_PASSWORD,
    UNMATCHING_PASSWORD,
)
from .models import User
from .tasks import send_email_verification_mail_async
from .validators import validate_password_for_user, verify_contact, verify_valid_mail




class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = User.get_hidden_fields()
        read_only_fields = User.read_only_fields(extra_fields=())
        extra_kwargs = {
            "email": {"required": False, "write_only": True},
            "user_type": {"read_only": True},
            "password": {"write_only": True, "required": False},
        }

    def validate_email(self, email):
        return verify_valid_mail(email)

    def validate_contact_no(self, contact):
        return verify_contact(contact)

    def validate(self, data):
        user_data = data.copy()
        user = User.from_validated_data(user_data)
        password = data.get("password")

        validate_password_for_user(password=password, user=user)
        return super(UserRegistrationSerializer, self).validate(data)

    def create(self, validated_data):
        first_name = validated_data.get("first_name")
        password = validated_data.get("password", None)
        if password is None:
            password = first_name
        validated_data["active"] = True
        user = super().create(validated_data)
        user.refresh_login_token(save=False)
        if password is None:
            raise serializers.ValidationError(INVALID_PASSWORD)
        user.set_password(password)
        user.save()
        send_email_verification_mail_async(user_id=user.id)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context["request"].user
        old_password = data["old_password"]
        new_password = data["new_password"]
        validate_password_for_user(password=new_password, user=user)
        if user:
            if not user.check_password(old_password):
                raise serializers.ValidationError(INCORRECT_OLD_PASSWORD)
        if old_password == new_password:
            raise serializers.ValidationError(UNMATCHING_PASSWORD)
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """
    This is used to serializer the email field
    """

    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            # We don't want to raise an exception here, due to the
            # security considerations
            # raise serializers.ValidationError("User does not exist")
            user = None
        data["user"] = user
        return data


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)


class NotificationSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        password = attrs.get("password")
        user = self.context.get("request").user
        is_password = user.check_password(password)
        if not is_password:
            raise ValidationError(INVALID_PASSWORD)
        return super().validate(attrs)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = User.get_hidden_fields()


class UserPrivateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = User.get_hidden_fields()
        read_only_fields = User.read_only_fields()
        write_only_fields = User.write_only_fields()
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserPublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "full_name", "image"]
        read_only_fields = ["first_name", "last_name", "full_name", "image"]


class ConfirmEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=10000)


class ResendVerificationMailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        login_data(data=data, user=user)
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        refresh.set_jti()
        refresh.set_exp()
        refresh.set_iat()

        data["refresh"] = str(refresh)
        self.user = User.objects.get(
            user_login_token=refresh.payload["user_login_token"]
        )
        # user_login_refreshed.send(sender=self.user.__class__, request=self.context['request'], user=self.user)

        return data




class UpdateUserFieldsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_null=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_null=True
    )
    contact_no = serializers.CharField(
        source="user.contact_no", required=False, allow_null=True
    )
    image = serializers.FileField(source="user.image", required=False, allow_null=True)
    date_of_birth = serializers.DateField(
        source="user.date_of_birth",
        required=False,
        allow_null=True,
    )
    gender = serializers.ChoiceField(
        source="user.gender", choices=Gender.choices, required=False
    )
    # email = serializers.EmailField(source="user.email", read_only=True)
    street = serializers.CharField(source="user.street", required=False)
    city = serializers.CharField(source="user.city", required=False)
    state = serializers.CharField(source="user.state", required=False)
    country = serializers.CharField(source="user.country", required=False)
    region = serializers.CharField(source="user.region", required=False)
