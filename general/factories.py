import factory
from core.factories import CoreFactory
from general.choices import ActionStatus

from .models import ContactUs, NewsletterSubscriber


STATUS_CHOICES = [x[0] for x in ActionStatus.choices]


class ContactUsFactory(CoreFactory):
    class Meta:
        model = ContactUs



class NewsletterSubscriberFactory(CoreFactory):
    class Meta:
        model = NewsletterSubscriber

    email = factory.Faker("email")
