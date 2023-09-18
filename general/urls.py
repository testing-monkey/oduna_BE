from django.urls import path

from .views import (
    ContactUsView,
    CreateNewsletterSubscriberAPIView,
    DeleteNewsletterSubscribersAPIView,
    ListNewsletterSubscribersAPIView,
    MediaListView,
    MediaView,
    NewsletterView
)

urlpatterns = [
   
    path("contact-us/", ContactUsView.as_view(), name="contact_us"),
     path(
        "newsletter-subscribers/",
        CreateNewsletterSubscriberAPIView.as_view(),
        name="subscribe-to-newsletter",
    ),
    path(
        "newsletter/subscribers/",
        ListNewsletterSubscribersAPIView.as_view(),
        name="list-newsletter-subscribers",
    ),
    path(
        "newsletter-subscribers/<uuid:pk>/",
        DeleteNewsletterSubscribersAPIView.as_view(),
        name="delete-newsletter-subscribers",
    ),
    path(
        "send-newsletter/",
        NewsletterView.as_view(),
        name="send_patient_newsletter",
    ),
    path("media/", MediaView.as_view(), name="media_list_create"),
    path("media/list", MediaListView.as_view(), name="media_list"),
]
