from django.urls import reverse

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientDetailTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        self.record = (
            self.create_client()
        )

    def test_detail_requires_authentication(
        self,
    ):
        response = self.client.get(
            self.detail_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_get_detail(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.detail_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        client = response.json()[
            "data"
        ]["client"]

        self.assertEqual(
            client["id"],
            self.record.pk,
        )

        self.assertEqual(
            client["phone_number"],
            "+250 788 000 000",
        )

        # Removed fields must not reappear in the response.
        for retired in (
            "slug",
            "company_name",
            "website",
            "location",
            "profile_image",
            "notes",
            "status",
            "phone",
        ):
            self.assertNotIn(
                retired,
                client,
            )

    def test_unknown_client_returns_404(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            reverse(
                "admin_api:client:detail",
                kwargs={
                    "client_id": 999999,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_detail_rejects_post(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.detail_url(
                self.record
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )
