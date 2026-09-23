from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)
from admin_api.tests.client.files import (
    image_upload,
)


class ClientAddTests(
    ClientApiTestCase
):
    def test_add_requires_authentication(
        self,
    ):
        response = self.client.post(
            self.add_url,
            {
                "name": "Example Client",
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_add_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.client.post(
            self.add_url,
            {
                "name": "Example Client",
            },
            **self.csrf_headers(),
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
            {
                "name": "Example Client",
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_create_client(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            {
                "name":
                    "GRACON Tech Holdings",
                "company_name":
                    "GRACON Tech Holdings Ltd",
                "email":
                    "info@example.com",
                "phone":
                    "+250788000000",
                "website":
                    "https://example.com",
                "location":
                    "Kigali, Rwanda",
                "notes":
                    "Important client.",
                "status":
                    Client.Status.ACTIVE,
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = (
            Client.objects.get(
                name=(
                    "GRACON Tech Holdings"
                )
            )
        )

        self.assertEqual(
            client.slug,
            "gracon-tech-holdings",
        )

        self.assertEqual(
            client.status,
            Client.Status.ACTIVE,
        )

    def test_client_can_be_created_with_image(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            {
                "name": "Image Client",
                "profile_image":
                    image_upload(),
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = (
            Client.objects.get(
                name="Image Client"
            )
        )

        self.assertTrue(
            client.profile_image
        )

    def test_name_is_required(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            {
                "company_name":
                    "Example Company",
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_status_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            {
                "name": "Client",
                "status": "unknown",
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            400,
        )
