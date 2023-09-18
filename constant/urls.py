from django.urls import path

from . import views

urlpatterns = [
    path("country/", view=views.Country.as_view(), name="country"),
    path("state/", view=views.State.as_view(), name="state"),
    path("city/", view=views.City.as_view(), name="city"),
]
