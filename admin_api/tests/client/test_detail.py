from django.urls import reverse

from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientDetailTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        self.domain_client = (
            Client.objects.create(
                name="Example Client",
                company_name=(
                    "Example Company"
                ),
                notes="Client notes.",
            )
        )

    def test_admin_can_get_detail(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.detail_url(
                self.domain_client
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
            self.domain_client.pk,
        )

        self.assertEqual(
            client["notes"],
            "Client notes.",
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
                self.domain_client
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )