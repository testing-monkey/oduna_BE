import base64
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

from core.utils import send_mail
from core.views import CoreGenericListView
from general.filters import MediaFilterBackend, NewsletterSubscriberFilterBackend
from general.literals import NEWSLETTER_EMAIL_SENT
from rest_framework.generics import DestroyAPIView, GenericAPIView, CreateAPIView
from general.tasks import send_newsletter

from user.permissions import AdminPermission

from .models import ContactUs, Media, NewsletterSubscriber
from .serializers import (
    ContactUsSerializer,
    MediaSerializer,
    NewsletterSerializer,
    NewsletterSubscribersSerializer,
)


class ContactUsView(APIView):
    """
    THIS API IS USED TO SEND MESSAGE TO THE ADMIN AND IS
    ACCESSIBLE BY ANY ONE
    """

    serializer_class = ContactUsSerializer()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        THIS API IS USED TO SEND MESSAGE TO THE ADMIN AND IS
        ACCESSIBLE BY ANY ONE. IT ACCESS VIA POST REQUEST AND THE EMAIL OF
        THE SENDER IS COLLECT FOR FEEDBACK PURPOSES
        """
        serializer = ContactUsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = serializer.validated_data["subject"]
        email = serializer.validated_data["email"]
        message = serializer.validated_data["message"]
        name = serializer.validated_data["name"]
        ContactUs.objects.create(
            name=name,
            subject=subject,
            email=email,
            message=message,
        )
        context = {"name": name, "text": message, "email": email}
        send_mail(
            subject=subject,
            to_email=settings.SUPPORT_EMAIL,
            input_context=context,
            template_name="emails/contact_us.html",
            bcc_list=settings.EXTRA_EMAILS,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "You message has been received and is been processed."},
        )


class CreateNewsletterSubscriberAPIView(CreateAPIView):
    """
    This API is used add user to newsletter.
    """

    schema_dict = {
        "summary": "Add Email to newsletter",
    }
    serializer_class = NewsletterSubscribersSerializer
    permission_classes = []


class ListNewsletterSubscribersAPIView(CoreGenericListView):
    """
    This API  Lists All Subscribed Newsletter Emails with filters and pagination included
    """

    schema_dict = {
        "summary": "Lists All Subscribed Newsletter Emails with filters and pagination included",
    }
    serializer_class = NewsletterSubscribersSerializer
    permission_classes = [AdminPermission]
    queryset = NewsletterSubscriber.objects.all()
    filterset_class = NewsletterSubscriberFilterBackend


class DeleteNewsletterSubscribersAPIView(DestroyAPIView):
    """
    This API Delete Email from newsletter
    """

    schema_dict = {
        "summary": "Delete Email from newsletter",
    }
    serializer_class = NewsletterSubscribersSerializer
    permission_classes = [AdminPermission]
    queryset = NewsletterSubscriber.objects.all()

    def perform_destroy(self, instance):
        _id = instance.id
        NewsletterSubscriber.all_objects.filter(id=_id).delete()


class NewsletterView(GenericAPIView):
    """
    This API Is used to send newsletter
    """

    schema_dict = {
        "summary": "Send Newsletter",
    }
    serializer_class = NewsletterSerializer
    permission_classes = [AdminPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = request.data
        emails = data["emails"]
        # emails = ["increaseodeyemi4@gmail.com","odeyemiincrease@yahoo.com"]
        message = data["message"]
        subject = data["subject"]
        file = data.get("file")
        byte = base64.b64encode(file.read()).decode("utf-8") if file else None

        newsletter_emails = NewsletterSubscriber.objects.filter(email__in=emails)
        emails = list(newsletter_emails.values_list("email", flat=True))
        send_newsletter(
            emails=emails,
            subject=subject,
            message=message,
            file=byte,
        )
        return Response(
            status=status.HTTP_200_OK, data={"message": NEWSLETTER_EMAIL_SENT}
        )


class MediaListView(CoreGenericListView):
    """
    This API is used to Lists  Media.
    """

    schema_dict = {
        "summary": "Lists an new  Media",
    }
    permission_classes = []
    serializer_class = MediaSerializer
    filterset_class = MediaFilterBackend
    queryset = Media.objects.filter()


class MediaView(ListCreateAPIView, RetrieveUpdateAPIView):
    permission_classes = [AdminPermission]
    serializer_class = MediaSerializer
    filterset_class = MediaFilterBackend
