from django.urls import reverse

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientUpdateTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        self.record = (
            self.create_client()
        )

    def test_update_requires_authentication(
        self,
    ):
        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {
                "name": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_update_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.patch(
            self.update_url(
                self.record
            ),
            data='{"name": "Renamed"}',
            content_type=(
                "application/json"
            ),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_partial_update(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {
                "phone_number": (
                    "+250 722 111 222"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.record.refresh_from_db()

        self.assertEqual(
            self.record.phone_number,
            "+250 722 111 222",
        )

        # Fields left out of the request keep their stored values.
        self.assertEqual(
            self.record.name,
            "Acme Rwanda",
        )

        self.assertEqual(
            self.record.email,
            "hello@acme.rw",
        )

    def test_empty_optional_field_clears_value(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {
                "email": "",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.json()["data"][
                "client"
            ]["email"]
        )

        self.record.refresh_from_db()

        self.assertEqual(
            self.record.email,
            "",
        )

    def test_empty_name_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {
                "name": "",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "name",
            response.json()["errors"],
        )

    def test_empty_payload_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_email_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.record
            ),
            {
                "email": "not-an-email",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.json()["errors"],
        )

    def test_unknown_client_returns_404(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            reverse(
                "admin_api:client:update",
                kwargs={
                    "client_id": 999999,
                },
            ),
            {
                "name": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_rejects_post(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.update_url(
                self.record
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )
