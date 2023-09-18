from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from general.factories import NewsletterSubscriberFactory
from general.literals import NEWSLETTER_EMAIL_SENT
from user.factories import AdminFactory, UserFactory

from .models import ContactUs, NewsletterSubscriber

# Create your tests here.


class TestContactUs(TestCase):
    def test_contact_us(self):
        data = {
            "name": "increase",
            "email": "odeyemiincrease@yahoo.com",
            "subject": "Cmplain",
            "message": "this is a random text",
        }
        url = reverse("general:contact_us")
        res = self.client.post(url, data=data, content_type="application/json")
        res_json = res.json()
        contact_messages = ContactUs.objects.all()
        contact_message = contact_messages.first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(contact_messages.count(), 1)
        self.assertEqual(contact_message.name, data["name"])
        self.assertEqual(contact_message.email, data["email"])
        self.assertEqual(contact_message.subject, data["subject"])
        self.assertEqual(contact_message.message, data["message"])
        self.assertTrue(
            res_json["message"], "You message has been received and is been processed."
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [settings.SUPPORT_EMAIL])
        self.assertEqual(mail.outbox[0].subject, data.get("subject"))


class NewsletterTest(TestCase):
    def test_send_newsletter_with_subscribed_user(self):
        user = AdminFactory()
        self.client.force_login(user)
        UserFactory.create_batch(4)
        NewsletterSubscriberFactory(email="mytestmail145@gmail.com")
        NewsletterSubscriberFactory(email="thinkalpha21@gmail.com")
        newsletters_emails = list(
            NewsletterSubscriber.objects.all().values_list("email", flat=True)
        )
        url = reverse("general:send_patient_newsletter")
        data = {
            "emails": newsletters_emails,
            "subject": "test subject",
            # "file": TEST_BASE64_IMGAGE,
            "message": "test message",
        }
        response = self.client.post(url, data=data, content_type="application/json")
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["message"], NEWSLETTER_EMAIL_SENT)
        self.assertEqual(mail.outbox[0].subject, data["subject"])
        self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER)
        self.assertTrue(data["emails"][0] in mail.outbox[0].to)
        self.assertTrue(data["emails"][1] in mail.outbox[0].to)
        self.assertEqual(response_data["message"], NEWSLETTER_EMAIL_SENT)

    def test_subscribed_to_newsletter(self):
        url = reverse("general:subscribe-to-newsletter")
        data = {"email": "increase@gmail.com"}
        response = self.client.post(url, data=data, content_type="application/json")
        response_data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data["email"], data.get("email"))
        data = {"email": "increase@gmail.com"}
        response = self.client.post(url, data=data, content_type="application/json")
        response_data = response.json()
        self.assertEqual(response.status_code, 400)

    def test_subscribed_to_newsletter_wrong_email(self):
        url = reverse("general:subscribe-to-newsletter")
        data = {"email": "increase"}
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_delete_subscribed_newsletter_emails(self):
        user = AdminFactory()
        self.client.force_login(user)
        newsletters = NewsletterSubscriberFactory.create_batch(5)
        url = reverse(
            "general:delete-newsletter-subscribers",
            kwargs={"pk": str(newsletters[0].id)},
        )
        response = self.client.delete(url)
        newsletters_from_db = NewsletterSubscriber.objects.all()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(newsletters_from_db.count(), len(newsletters) - 1)
        url = reverse("general:subscribe-to-newsletter")
        data = {"email": newsletters[0].email}
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_list_subscribed_newsletter_emails(self):
        user = AdminFactory()
        self.client.force_login(user)
        Newsletters = NewsletterSubscriberFactory.create_batch(5)
        url = reverse("general:list-newsletter-subscribers")
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data["results"]), len(Newsletters))

    def test_list_subscribed_newsletter_emails_by_unauth_user(self):
        url = reverse("general:list-newsletter-subscribers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)