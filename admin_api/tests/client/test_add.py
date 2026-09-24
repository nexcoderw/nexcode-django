from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientAddTests(
    ClientApiTestCase
):
    def payload(
        self,
        **overrides,
    ):
        data = {
            "name": "Acme Rwanda",
            "email": "hello@acme.rw",
            "phone_number": (
                "+250 788 000 000"
            ),
        }

        data.update(overrides)

        return data

    def test_add_requires_authentication(
        self,
    ):
        response = self.post_json(
            self.add_url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertFalse(
            Client.objects.exists()
        )

    def test_add_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.post_json(
            self.add_url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_add_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            data="{}",
            content_type=(
                "application/json"
            ),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_create_client(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = response.json()[
            "data"
        ]["client"]

        # The contract is exactly these fields and no others.
        self.assertEqual(
            set(client),
            {
                "id",
                "name",
                "email",
                "phone_number",
                "created_at",
                "updated_at",
            },
        )

        self.assertEqual(
            client["name"],
            "Acme Rwanda",
        )

        self.assertEqual(
            client["email"],
            "hello@acme.rw",
        )

        self.assertEqual(
            client["phone_number"],
            "+250 788 000 000",
        )

    def test_contact_details_are_optional(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            {
                "name": "Walk-in client",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = response.json()[
            "data"
        ]["client"]

        self.assertIsNone(
            client["email"]
        )

        self.assertIsNone(
            client["phone_number"]
        )

    def test_name_is_required(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                name="",
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "name",
            response.json()["errors"],
        )

        self.assertFalse(
            Client.objects.exists()
        )

    def test_invalid_email_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                email="not-an-email",
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.json()["errors"],
        )

    def test_non_json_request_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            data={
                "name": "Form post",
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            415,
        )

    def test_add_rejects_get(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.add_url
        )

        self.assertEqual(
            response.status_code,
            405,
        )
