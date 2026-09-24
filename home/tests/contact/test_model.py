from django.test import (
    TestCase,
)

from home.models import Contact


class ContactModelTests(
    TestCase
):
    def test_contact_stores_submission(
        self,
    ):
        contact = (
            Contact.objects.create(
                name="Jane Doe",
                email=(
                    "jane@example.com"
                ),
                subject=(
                    "Project enquiry"
                ),
                message=(
                    "I would like to "
                    "discuss a project."
                ),
            )
        )

        self.assertEqual(
            contact.name,
            "Jane Doe",
        )

        self.assertEqual(
            contact.email,
            "jane@example.com",
        )

        self.assertEqual(
            contact.subject,
            "Project enquiry",
        )

        self.assertEqual(
            contact.message,
            (
                "I would like to "
                "discuss a project."
            ),
        )

        self.assertIsNotNone(
            contact.created_at
        )

    def test_string_representation(
        self,
    ):
        contact = (
            Contact.objects.create(
                name="Jane Doe",
                email=(
                    "jane@example.com"
                ),
                subject=(
                    "Project enquiry"
                ),
                message="Hello",
            )
        )

        self.assertEqual(
            str(contact),
            (
                "Project enquiry — "
                "Jane Doe"
            ),
        )

    def test_newest_contacts_are_first(
        self,
    ):
        first = (
            Contact.objects.create(
                name="First",
                email=(
                    "first@example.com"
                ),
                subject="First",
                message="First",
            )
        )

        second = (
            Contact.objects.create(
                name="Second",
                email=(
                    "second@example.com"
                ),
                subject="Second",
                message="Second",
            )
        )

        contacts = list(
            Contact.objects.all()
        )

        self.assertEqual(
            contacts,
            [
                second,
                first,
            ],
        )