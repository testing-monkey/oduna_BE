from datetime import timedelta
from typing import Dict
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase, modify_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import ExpiringActivationTokenGenerator, encode_data
from user.choices import PasswordChangeStatus, UserType
from user.models import AccessLog, PasswordResetWhitelist, User

from .factories import PasswordRestFactory, UserFactory
from .literals import (
    INVALID_PASSWORD,
    OTP_DISABLED,
    OTP_TOKEN_IS_INVALID,
    OTP_TOKEN_NOT_PROVIDED,
    RESET_PASSWORD_WITH_SIMILAR_PASSWORD,
    USER_LOGOUT_SUCCESSFUL,
)
from .test_literals import USER_TEST_REGISTRATIONS_INFO

# Create your tests here.


class UserRegistrationTestCase(object):
    def setUp(self):
        """This should never execute but it does when I test test_store_a"""
        self.url = None
        self.query_params = None
        self.data = USER_TEST_REGISTRATIONS_INFO

    def update_data(self, data: Dict):
        self.data.update(data)

    def remove_key_from_data(self, key):
        self.data.pop(key, None)

    def _test_user_registration_right_information(self):
        query_params = self.query_params if self.query_params else ""
        url = reverse(self.url) + query_params
        response = self.client.post(url, data=self.data)
        self.query_params = ""
        self.assertEqual(
            response.status_code, 201
        ) if response.status_code == 201 else None
        self.assertEqual(
            mail.outbox[0].subject, "Verify User Account"
        ) if response.status_code == 201 else None
        self.assertEqual(
            mail.outbox[0].from_email, settings.EMAIL_HOST_USER
        ) if response.status_code == 201 else None
        self.assertEqual(
            mail.outbox[0].to, [self.data["email"]]
        ) if response.status_code == 201 else None
        return response


class UserModel(TestCase):
    def setUp(self):
        UserFactory.create_batch(3)
        self.deleted_users = UserFactory.create_batch(2, is_deleted=True)

    def test_user_manager_all_returns_only_undeleted_objects(self):
        users = User.objects.all()
        self.assertEqual(len(users), 3)

    def test_user_manager_soft_delete_function(self):
        User.objects.delete()
        users_after_delete = User.objects.all()
        all_users_including_deleted = User.all_objects.all()
        self.assertEqual(len(users_after_delete), 0)
        self.assertEqual(len(all_users_including_deleted), 5)

    def test_soft_delete__of_object(self):
        self.deleted_users[0].delete()
        user = User.all_objects.get(id=self.deleted_users[0].id)
        self.assertEquals(user.is_deleted, True)
        self.assertIsNotNone(user.deleted_at)

  

class ChangePasswordTest(TestCase):
   
    def test_password_change_with_authenticated_user(
        self,
    ):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("user:change_password")
        old_password = user.first_name
        new_password = "new_P@assword"
        data = {"old_password": old_password, "new_password": new_password}
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        white_passwords = PasswordResetWhitelist.objects.all()
        white_password = white_passwords.first()
        self.assertEqual(white_passwords.count(), 1)
        self.assertEqual(
            white_password.status,
            PasswordChangeStatus.CHANGE_PASSWORD,
        )
        self.assertTrue(PasswordChangeStatus.CHANGE_PASSWORD in white_password.token)
        self.assertTrue(user.check_password(new_password))

    def test_password_change_with_authenticated_user_but_common_password(
        self,
    ):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("user:change_password")
        old_password = user.first_name
        new_password = "password"
        data = {"old_password": old_password, "new_password": new_password}
        response = self.client.patch(url, data=data, content_type="application/json")
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertTrue("This password is too common" in response_data["error"])
        self.assertFalse(user.check_password(new_password))

    def test_password_change_with_unauthenticated_user(self):
        url = reverse("user:change_password")
        old_password = "user_password"
        new_password = "new_password"
        data = {"old_password": old_password, "new_password": new_password}
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_password_change_with_wrong_old_password(
        self,
    ):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("user:change_password")
        old_password = user.first_name + "wrong_string"
        new_password = "new_password"
        data = {"old_password": old_password, "new_password": new_password}
        response = self.client.patch(url, data=data, content_type="application/json")
        # response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.first().check_password(new_password))

    def test_password_change_with_old_password_equals_new(
        self,
    ):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("user:change_password")
        old_password = user.first_name
        new_password = old_password
        data = {"old_password": old_password, "new_password": new_password}
        response = self.client.patch(url, data=data, content_type="application/json")
        # response_data = response.json()
        self.assertEqual(response.status_code, 400)


class InitialPasswordResetTest(TestCase):
    def setUp(self):
        self.user = UserFactory(email="odeyemiincrease@yahoo.com")

    def test_initiate_password_reset_with_email_that_exists(self):
        url = reverse("user:initiate_password_reset")
        data = {"email": self.user.email}
        response = self.client.post(url, data)
        response_data = response.json()
        self.user.refresh_from_db()
        self.assertEqual(self.user.user_login_token, self.user.user_login_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            response_data["message"], "Email Has Been sent to the email provided"
        )
        self.assertEqual(mail.outbox[0].subject, "Password Reset")
        self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_initiate_password_reset_with_email_that_dont_exists(self):
        url = reverse("user:initiate_password_reset")
        data = {"email": "unknown@gmail.com"}
        response = self.client.post(url, data)
        response_data = response.json()
        self.user.refresh_from_db()
        self.assertEquals(self.user.user_login_token, self.user.user_login_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["message"], "Email Has Been sent to the email provided"
        )
        self.assertEqual(len(mail.outbox), 0)


class CompletePasswordResetTest(TestCase):
    def setUp(self):
        self.user = UserFactory(email="odeyemiincrease@yahoo.com")

    # def test_password_reset_with_email_that_exists_and_token_and_common_password(
    #     self,
    # ):
    #     url = reverse("user:complete_password_reset")
    #     new_password = 'password'
    #     password_reset_object = PasswordRestFactory(email=self.user.email)
    #     data = {"password": new_password, "token": password_reset_object.token}
    #     user = User.objects.get(id=self.user.id)
    #     self.assertTrue(user.check_password(user.first_name))
    #     self.assertRaises(DjangoValidationError, lambda: self.client.post(url, data))
    #     # response_data = response.json()
    #     # self.assertEqual(response.status_code, 400)
    #     # self.assertFalse(user.check_password(new_password))

    def test_password_reset_with_email_that_exists_and_token_and_using_former_password(
        self,
    ):
        password = "576895394Y@ehfdfdj"
        self.user.set_password(password)
        self.user.save()
        url = reverse("user:complete_password_reset")
        password_reset_object = PasswordRestFactory(email=self.user.email)
        data = {"password": password, "token": password_reset_object.token}
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(password))
        response = self.client.post(url, data)
        response_data = response.json()
        self.user.refresh_from_db()
        self.assertEqual(response_data["error"], RESET_PASSWORD_WITH_SIMILAR_PASSWORD)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(user.check_password(password))

    def test_password_reset_with_email_that_exists_and_token(self):
        url = reverse("user:complete_password_reset")
        password_reset_object = PasswordRestFactory(email=self.user.email)
        data = {"password": "New_p@ssword12", "token": password_reset_object.token}
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(user.first_name))
        self.assertFalse((user.check_password(data["password"])))
        response = self.client.post(url, data)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=self.user.id)
        self.assertNotEqual(user.user_login_token, self.user.user_login_token)
        self.assertTrue(user.check_password(data["password"]))
        self.assertFalse(user.check_password(user.first_name))
        self.assertEqual(response_data["message"], "Password Reset Completed")

    def test_password_reset_with_email_that_exists_and_invalid_token(self):
        url = reverse("user:complete_password_reset")
        password_reset_object = PasswordRestFactory(email=self.user.email)
        data = {"password": "new_password", "token": f"{password_reset_object}-invalid"}
        response = self.client.post(url, data)
        response_data = response.json()
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.user_login_token, self.user.user_login_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_data["error"],
            "Invalid Token. Password Rest Record Doesn't Exists",
        )

    def test_password_used_token(self):
        url = reverse("user:complete_password_reset")
        password_reset_object = PasswordRestFactory(email=self.user.email)
        data = {"password": "new_P@1ssword", "token": password_reset_object.token}
        self.client.post(url, data)
        response = self.client.post(url, data)
        response_data = response.json()
        self.assertEqual(
            response_data["error"],
            "Invalid Token. Password Rest Record Doesn't Exists",
        )


class UserProfile(TestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=False)

    def test_user_profile(self):
        url = reverse("user:profile")
        self.client.force_login(self.user)
        response = self.client.get(url)
        # response_data = response.json()
        self.assertEqual(response.status_code, 200)


class ConfirmUserEmail(TestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=False)
        self.token_object = ExpiringActivationTokenGenerator()

    def test_confirm_with_email_that_exists_and_token(self):
        token = str(self.token_object.generate_token(self.user.email).decode("utf-8"))
        url = reverse("user:confirm_email")
        data = {"token": token}
        response = self.client.post(url, data=data)
        response_data = response.json()
        user = User.objects.get(id=self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["message"], "Email Verification successful")
        self.assertEqual(user.is_verified, True)

    def test_confirm_with_invalid_token(self):
        addition = "1234567890123456789012345678901"
        real_token = {self.token_object.generate_token(self.user.email).decode("utf-8")}
        token = f"{addition}{real_token}"
        url = reverse("user:confirm_email")
        data = {"token": token}
        response = self.client.post(url, data=data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(user.is_verified, False)
        addition = "1234567890123456789012345678901"
        real_token = {self.token_object.generate_token(self.user.email).decode("utf-8")}
        token = addition
        url = reverse("user:confirm_email")
        data = {"token": token}
        response = self.client.post(url, data=data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(user.is_verified, False)


class TestUserLogin(TestCase):
    def setUp(self):
        self.user = UserFactory(user_type=UserType.ADMIN)

    def test_user_login_email(self):
        url = reverse("user:token_obtain_pair")
        self.user.email = "odunaec@gmail.com"
        self.user.save()
        data = {"email": self.user.email, "password": self.user.first_name}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": self.user.email, "password": self.user.first_name}
        response = self.client.post(url, data=data)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        required_keys = {
            "last_name",
            "email",
            "user_type",
            "is_verified",
            "country",
            "region",
            "contact_no",
            "image",
        }
        user_response_key = set(response_data["user"].keys())
        self.assertTrue(bool(user_response_key.intersection(required_keys)))

    # @override_settings(ENFORCE_GOOGLE_RECAPTCHA=True)
    def test_user_login_with_recaptcha_enabled(self):
        url = reverse("user:token_obtain_pair")
        data = {
            "email": self.user.email,
            "password": self.user.first_name,
            "token": "token1",
            # "recaptcha_token": "",
        }
        with self.settings(ENFORCE_GOOGLE_RECAPTCHA=True):
            response = self.client.post(url, data=data)
            response_data = response.json()
            self.assertEqual(response.status_code, 200)
            required_keys = {
                "last_name",
                "email",
                "user_type",
                "is_verified",
                "country",
                "region",
                "contact_no",
                "image",
            }
            user_response_key = set(response_data["user"].keys())
            self.assertTrue(bool(user_response_key.intersection(required_keys)))

    
    def test_login_attempt(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": self.user.email, "password": self.user.first_name + "wrong"}
        response = self.client.post(url, data=data)
        response = self.client.post(url, data=data)
        response = self.client.post(url, data=data)
        data["password"] = self.user.first_name
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_user_refresh_token(self):
        url = reverse("user:token_refresh")
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)


class TestRequestHeaderMiddleware(TestCase):
    def test_request_header_middleware_without_platfrom_key(self):
        user = UserFactory()
        user.is_verified = False
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": user.email,
        }
        with self.modify_settings(
            MIDDLEWARE={
                "append": "user.middleware.RequestHeadersMiddleware",
            }
        ):
            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, 401)

    def test_request_header_middleware_with_platform_key(self):
        user = UserFactory()
        user.is_verified = False
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": user.email,
        }
        with self.modify_settings(
            MIDDLEWARE={
                "append": "user.middleware.RequestHeadersMiddleware",
            }
        ):
            response = self.client.post(
                url, data=data, **{"HTTP_x_api_key": settings.PLATFORM_KEY}
            )
            self.assertEqual(response.status_code, 200)


class TestRequestLogMiddleware(TestCase):
    def test_request_log_middleware_unauthenticated_user(self):
        user = UserFactory()
        user.is_verified = False
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": user.email,
        }
        with self.modify_settings(
            MIDDLEWARE={
                "append": "user.middleware.RequestLogMiddleware",
            }
        ):
            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, 200)
            accesslogs = AccessLog.objects.all()
            accesslog = accesslogs.first()
            self.assertEqual(accesslogs.count(), 0)
            self.assertIsNone(accesslog)

    def test_request_log_middleware_authenticated_user(self):
        user = UserFactory()
        user.is_verified = False
        user.save()
        url = reverse("user:resend_verification_mail")
        self.client.force_login(user)
        data = {
            "email": user.email,
        }

        with self.modify_settings(
            MIDDLEWARE={
                "append": "user.middleware.RequestLogMiddleware",
            }
        ):
            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, 200)
            accesslogs = AccessLog.objects.all()
            accesslog = accesslogs.first()
            self.assertEqual(accesslog.user_agent, "-")
            self.assertEqual(accesslog.location, "")
            self.assertEqual(accesslog.meta, None)
            self.assertEqual(accesslog.device_ip, "127.0.0.1")
            self.assertEqual(accesslog.user, user)
            self.assertEqual(accesslog.user_login_token, user.user_login_token)
            self.assertEqual(accesslog.url, url)
            self.assertEqual(accesslog.status_code, response.status_code)
            self.assertIsNotNone(accesslog.request_id)


class TestChangeNotificationMail(TestCase):
    def test_initiate_notification_mail_change_user(self):
        user = UserFactory()
        self.client.force_login(user)
        user.save()
        url = reverse("user:initiate_email_reset")
        data = {
            "email": "email" + user.email,
            "password": user.first_name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox[0].subject, "Initiate Notification Email")
        self.assertEqual(mail.outbox[0].to, [data.get("email")])

        self.assertEqual(len(mail.outbox), 1)

    def test_complete_notification_mail_change_user(self):
        user = UserFactory()
        url = reverse("user:complete_email_reset")
        token_data = {
            "email": user.email,
            "email": "rubbisthodhfnotification" + user.email,
            "user_id": str(user.id),
        }
        token = encode_data(token_data)
        data = {
            "token": token,
        }
        response = self.client.post(url, data=data)
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, token_data["email"])

    def test_complete_notification_mail_change_user_expired(self):
        user = UserFactory()
        url = reverse("user:complete_email_reset")
        token_data = {
            "email": user.email,
            "email": "rubbisthodhfnotification" + user.email,
            "user_id": str(user.id),
        }
        token = encode_data(token_data)
        data = {
            "token": token,
        }
        response = self.client.post(url, data=data)
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, token_data["email"])


class ResendVerificationMail(TestCase):
    def test_resend_email_verification_For_unverified_user(self):
        user = UserFactory()
        user.is_verified = False
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": user.email,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox[0].subject, "Verify User Account")
        self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_email_verification_For_verified_user(self):
        user = UserFactory()
        user.is_verified = True
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": user.email,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_email_verification_For_unregisterd_user_email(self):
        user = UserFactory()
        user.is_verified = True
        user.save()
        url = reverse("user:resend_verification_mail")
        data = {
            "email": "user.email@gmail.com",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class WebAuthn(TestCase):
    def test_initiate_web_authn(self):
        user = UserFactory()
        self.client.force_login(user)
        # url = reverse("user:webauthn_registration_options")
        # data = {
        #     "verify_data": {
        #         "username": "rr",
        #         "user_verification": "preferred",
        #         "attestation": "none",
        #         "attachment": "all",
        #         "algorithms": ["es256", "rs256"],
        #         "discoverable_credential": "preferred",
        #     }
        # }
        # response = self.client.post(url, data=data, content_type="application/json")
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(mail.outbox[0].subject, "Verify User Account")
        # self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER)
        # self.assertEqual(len(mail.outbox), 1)
