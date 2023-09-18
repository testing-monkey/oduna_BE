from unittest import mock

from django.test import TestCase


# Create your tests here.
class CustomTestCase(TestCase):
    def __call__(self, result) -> None:
        with mock.patch("django.core.files.storage.Storage.save", return_value="name"):
            with self.settings(
                CACHES={
                    "default": {
                        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                        "LOCATION": "unique-snowflake",
                    }
                }
            ):
                return super().__call__(result)
