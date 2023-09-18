import uuid
from datetime import date, datetime, timedelta

import factory
from django.conf import settings
from django.contrib.auth.hashers import make_password
from factory import fuzzy

from core.factories import CoreFactory
from core.utils import ExpiringActivationTokenGenerator
from user.choices import Gender, UserType
from user.models import PasswordResetWhitelist, User

GENDER_CHOICES = [x[0] for x in Gender.choices]
REGION_CHOICES = [x[0] for x in User.UserRegion.choices]



default_password = "Password@123" if not settings.TESTING else None


class UserFactory(CoreFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        exclude = ("now",)

    now = factory.LazyFunction(datetime.utcnow)
    date_of_birth = factory.LazyAttribute(lambda o: o.now - timedelta(weeks=1400))
    user_login_token = factory.LazyAttribute(lambda o:  "-" + uuid.uuid4().hex)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    contact_no = factory.Faker("phone_number")
    password = factory.LazyAttribute(
        lambda user: make_password(default_password or user.first_name)
    )
    gender = fuzzy.FuzzyChoice(GENDER_CHOICES)
    region = fuzzy.FuzzyChoice(REGION_CHOICES)

    image = factory.django.ImageField() if settings.TESTING else None
    date_of_birth = fuzzy.FuzzyDate(date(1945, 1, 1))
    is_deleted = False
    is_verified = True


class AdminFactory(UserFactory):
    user_type = UserType.ADMIN


class StaffUserFactory(UserFactory):
    user_type = UserType.DEVELOPER
    is_staff = True


class SuperUserFactory(StaffUserFactory):
    is_superuser = True


class PasswordRestFactory(CoreFactory):
    class Meta:
        model = PasswordResetWhitelist

    email = factory.Faker("email")
    token = factory.LazyAttribute(
        lambda object: ExpiringActivationTokenGenerator()
        .generate_token(text=object.email)
        .decode("utf-8")
    )

 