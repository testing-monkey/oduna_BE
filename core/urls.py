from django.urls import path

from .views import LoggingTest

urlpatterns = [
    path("test-logging/", LoggingTest.as_view(), name="logging-test"),
]
