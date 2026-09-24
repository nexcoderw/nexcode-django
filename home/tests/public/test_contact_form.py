"""Visitors send messages from the contact page; the sender is recorded."""

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from home.contact_throttle import CONTACT_MAX_SUBMISSIONS
from home.models import Contact


ANDROID_PHONE = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
)


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ContactFormTests(TestCase):
    def setUp(self):
        # Submissions are throttled per address; start each test afresh.
        cache.clear()
        self.url = reverse("base:contact")

    def payload(self, **overrides):
        data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Project enquiry",
            "message": "I would like to discuss a project.",
            "website": "",
        }
        data.update(overrides)
        return data

    def submit(self, **overrides):
        return self.client.post(
            self.url,
            self.payload(**overrides),
            HTTP_X_REAL_IP="203.0.113.9",
            HTTP_USER_AGENT=ANDROID_PHONE,
        )

    def test_page_shows_the_form_and_contact_details(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for field in ("name", "email", "subject", "message"):
            self.assertContains(response, f'name="{field}"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, 'href="tel:+250781862349"')

    def test_submission_is_saved_with_the_sender_details(self):
        response = self.submit()

        self.assertRedirects(response, self.url)

        contact = Contact.objects.get()
        self.assertEqual(contact.name, "Jane Doe")
        self.assertEqual(contact.email, "jane@example.com")
        self.assertEqual(contact.subject, "Project enquiry")
        self.assertEqual(contact.message, "I would like to discuss a project.")
        self.assertEqual(contact.ip_address, "203.0.113.9")
        self.assertEqual(contact.device_type, Contact.DeviceType.MOBILE)
        self.assertEqual(contact.browser, "Chrome")
        self.assertEqual(contact.operating_system, "Android")
        self.assertIsNone(contact.replied_at)

    def test_visitor_is_told_the_message_was_sent(self):
        response = self.client.post(
            self.url, self.payload(), follow=True
        )

        messages = [str(message) for message in response.context["messages"]]
        self.assertEqual(len(messages), 1)
        self.assertIn("jane@example.com", messages[0])

    def test_invalid_submission_shows_errors_and_keeps_the_input(self):
        response = self.submit(email="not-an-email", message="")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contact.objects.exists())
        self.assertIn("email", response.context["form"].errors)
        self.assertIn("message", response.context["form"].errors)
        # What the visitor typed is still there to correct.
        self.assertContains(response, 'value="Jane Doe"')

    def test_honeypot_submissions_are_discarded(self):
        response = self.submit(website="https://spam.example")

        self.assertRedirects(response, self.url)
        self.assertFalse(Contact.objects.exists())

    def test_repeated_submissions_are_throttled(self):
        for _ in range(CONTACT_MAX_SUBMISSIONS):
            self.assertEqual(self.submit().status_code, 302)

        response = self.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have sent several messages recently")
        self.assertEqual(Contact.objects.count(), CONTACT_MAX_SUBMISSIONS)

    def test_submission_requires_csrf(self):
        client = self.client_class(enforce_csrf_checks=True)

        response = client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Contact.objects.exists())
