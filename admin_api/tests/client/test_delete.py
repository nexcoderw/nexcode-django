from django.urls import reverse

from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientDeleteTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        self.record = (
            self.create_client()
        )

    def test_delete_requires_authentication(
        self,
    ):
        response = self.delete_request(
            self.delete_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertTrue(
            Client.objects.filter(
                pk=self.record.pk
            ).exists()
        )

    def test_delete_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.delete_request(
            self.delete_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_delete_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.delete(
            self.delete_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertTrue(
            Client.objects.filter(
                pk=self.record.pk
            ).exists()
        )

    def test_admin_can_delete_client(
        self,
    ):
        self.login_admin()

        response = self.delete_request(
            self.delete_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            Client.objects.filter(
                pk=self.record.pk
            ).exists()
        )

    def test_unknown_client_returns_404(
        self,
    ):
        self.login_admin()

        response = self.delete_request(
            reverse(
                "admin_api:client:delete",
                kwargs={
                    "client_id": 999999,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_delete_rejects_get(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.delete_url(
                self.record
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
