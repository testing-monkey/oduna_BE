
from core.filters import CoreFilterBackend

from .models import ContactUs, NewsletterSubscriber, Media

class ContactUsFilterBackend(CoreFilterBackend):
    class Meta:
        model = ContactUs
        fields = "__all__"

class NewsletterSubscriberFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = NewsletterSubscriber
        fields = "__all__"

class MediaFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = Media
        exclude = ["file"]

