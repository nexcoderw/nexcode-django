from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)
from admin_api.tests.team.files import (
    image_upload,
)


class TeamUpdateTests(
    TeamApiTestCase
):
    def setUp(self):
        super().setUp()

        self.member = (
            Team.objects.create(
                name="Alice",
                position="Developer",
                image_png=image_upload(
                    "old.png"
                ),
            )
        )

    def test_update_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.patch(
            self.update_url(
                self.member
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
                    self.member
                ),
                {
                    "position":
                        "Senior Developer",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.member.refresh_from_db()

        self.assertEqual(
            self.member.position,
            "Senior Developer",
        )

        self.assertEqual(
            self.member.name,
            "Alice",
        )

    def test_empty_name_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.update_url(
                    self.member
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

    def test_replacing_image_deletes_old_file(
        self,
    ):
        self.login_admin()

        old_name = (
            self.member
            .image_png
            .name
        )

        storage = (
            self.member
            .image_png
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
                        self.member
                    ),
                    {
                        "image_png":
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

    def test_remove_image(
        self,
    ):
        self.login_admin()

        old_name = (
            self.member
            .image_png
            .name
        )

        storage = (
            self.member
            .image_png
            .storage
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            response = (
                self.patch_multipart(
                    self.update_url(
                        self.member
                    ),
                    {
                        "remove_image_png":
                            "true",
                    },
                )
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.member.refresh_from_db()

        self.assertFalse(
            self.member.image_png
        )

        self.assertFalse(
            storage.exists(
                old_name
            )
        )