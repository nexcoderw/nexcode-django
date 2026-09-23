from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)
from admin_api.tests.client.files import (
    image_upload,
)


class ClientUpdateTests(
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
                email=(
                    "client@example.com"
                ),
                profile_image=(
                    image_upload(
                        "old.png"
                    )
                ),
            )
        )

    def test_update_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.patch(
            self.update_url(
                self.domain_client
            ),
            data=b"",
            content_type=(
                "multipart/form-data"
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

        response = (
            self.patch_multipart(
                self.update_url(
                    self.domain_client
                ),
                {
                    "company_name":
                        "Updated Company",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.domain_client.refresh_from_db()

        self.assertEqual(
            self.domain_client
            .company_name,
            "Updated Company",
        )

        self.assertEqual(
            self.domain_client.name,
            "Example Client",
        )

    def test_slug_remains_stable_when_name_changes(
        self,
    ):
        self.login_admin()

        original_slug = (
            self.domain_client.slug
        )

        response = (
            self.patch_multipart(
                self.update_url(
                    self.domain_client
                ),
                {
                    "name":
                        "Renamed Client",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.domain_client.refresh_from_db()

        self.assertEqual(
            self.domain_client.slug,
            original_slug,
        )

    def test_empty_name_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.update_url(
                    self.domain_client
                ),
                {
                    "name": "",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_status_can_be_changed(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.update_url(
                    self.domain_client
                ),
                {
                    "status":
                        Client.Status
                        .INACTIVE,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.domain_client.refresh_from_db()

        self.assertEqual(
            self.domain_client.status,
            Client.Status.INACTIVE,
        )

    def test_replacing_profile_image_deletes_old_file(
        self,
    ):
        self.login_admin()

        old_name = (
            self.domain_client
            .profile_image
            .name
        )

        storage = (
            self.domain_client
            .profile_image
            .storage
        )

        self.assertTrue(
            storage.exists(
                old_name
            )
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            response = (
                self.patch_multipart(
                    self.update_url(
                        self.domain_client
                    ),
                    {
                        "profile_image":
                            image_upload(
                                "new.png"
                            ),
                    },
                )
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            storage.exists(
                old_name
            )
        )

    def test_remove_profile_image(
        self,
    ):
        self.login_admin()

        old_name = (
            self.domain_client
            .profile_image
            .name
        )

        storage = (
            self.domain_client
            .profile_image
            .storage
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            response = (
                self.patch_multipart(
                    self.update_url(
                        self.domain_client
                    ),
                    {
                        "remove_profile_image":
                            "true",
                    },
                )
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.domain_client.refresh_from_db()

        self.assertFalse(
            self.domain_client
            .profile_image
        )

        self.assertFalse(
            storage.exists(
                old_name
            )
        )

    def test_empty_optional_field_clears_value(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.update_url(
                    self.domain_client
                ),
                {
                    "email": "",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.domain_client.refresh_from_db()

        self.assertEqual(
            self.domain_client.email,
            "",
        )