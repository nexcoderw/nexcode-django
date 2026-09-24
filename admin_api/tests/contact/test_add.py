import json

from django.test import (
    Client as DjangoClient,
    TestCase,
)
from django.urls import reverse

from home.models import Contact


class ContactAddTests(
    TestCase
):
    def setUp(self):
        self.client = (
            DjangoClient(
                enforce_csrf_checks=True,
            )
        )

        self.add_url = reverse(
            "admin_api:contact:add"
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

    def payload(
        self,
        **overrides,
    ):
        data = {
            "name":
                "Jane Doe",

            "email":
                "jane@example.com",

            "subject":
                "Project enquiry",

            "message": (
                "I would like to "
                "discuss a project."
            ),
        }

        data.update(
            overrides
        )

        return data

    def csrf_token(self):
        response = (
            self.client.get(
                self.csrf_url
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        return response.json()[
            "data"
        ]["csrf_token"]

    def post_json(
        self,
        payload,
    ):
        token = (
            self.csrf_token()
        )

        return self.client.post(
            self.add_url,
            data=json.dumps(
                payload
            ),
            content_type=(
                "application/json"
            ),
            HTTP_X_CSRFTOKEN=(
                token
            ),
        )

    def test_customer_can_submit_without_authentication(
        self,
    ):
        response = (
            self.post_json(
                self.payload()
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            Contact.objects.count(),
            1,
        )

    def test_submission_is_saved(
        self,
    ):
        response = (
            self.post_json(
                self.payload()
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        contact = (
            Contact.objects.get()
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

    def test_response_contract(
        self,
    ):
        response = (
            self.post_json(
                self.payload()
            )
        )

        contact = (
            response.json()[
                "data"
            ]["contact"]
        )

        self.assertEqual(
            set(contact),
            {
                "id",
                "name",
                "email",
                "subject",
                "message",
                "created_at",
            },
        )

    def test_name_is_required(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    name="",
                )
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "name",
            response.json()[
                "errors"
            ],
        )

        self.assertFalse(
            Contact.objects.exists()
        )

    def test_email_is_required(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    email="",
                )
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.json()[
                "errors"
            ],
        )

    def test_invalid_email_is_rejected(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    email=(
                        "not-an-email"
                    ),
                )
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.json()[
                "errors"
            ],
        )

    def test_subject_is_required(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    subject="",
                )
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "subject",
            response.json()[
                "errors"
            ],
        )

    def test_message_is_required(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    message="",
                )
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "message",
            response.json()[
                "errors"
            ],
        )

    def test_fields_are_trimmed(
        self,
    ):
        response = (
            self.post_json(
                self.payload(
                    name=(
                        "  Jane Doe  "
                    ),
                    subject=(
                        "  Hello  "
                    ),
                    message=(
                        "  My message  "
                    ),
                )
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        contact = (
            Contact.objects.get()
        )

        self.assertEqual(
            contact.name,
            "Jane Doe",
        )

        self.assertEqual(
            contact.subject,
            "Hello",
        )

        self.assertEqual(
            contact.message,
            "My message",
        )

    def test_unknown_fields_are_not_saved(
        self,
    ):
        response = (
            self.post_json(
                {
                    **self.payload(),
                    "is_admin": True,
                    "created_at":
                        "2000-01-01",
                }
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        contact = (
            Contact.objects.get()
        )

        self.assertFalse(
            hasattr(
                contact,
                "is_admin",
            )
        )

    def test_submission_requires_csrf(
        self,
    ):
        response = (
            self.client.post(
                self.add_url,
                data=json.dumps(
                    self.payload()
                ),
                content_type=(
                    "application/json"
                ),
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertFalse(
            Contact.objects.exists()
        )

    def test_non_json_request_is_rejected(
        self,
    ):
        token = (
            self.csrf_token()
        )

        response = (
            self.client.post(
                self.add_url,
                data={
                    "name":
                        "Jane Doe",
                },
                HTTP_X_CSRFTOKEN=(
                    token
                ),
            )
        )

        self.assertEqual(
            response.status_code,
            415,
        )

    def test_get_is_rejected(
        self,
    ):
        response = (
            self.client.get(
                self.add_url
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

        self.assertEqual(
            response[
                "Allow"
            ],
            "POST",
        )