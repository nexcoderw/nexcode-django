from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)
from admin_api.tests.team.files import (
    image_upload,
)


class TeamDeleteTests(
    TeamApiTestCase
):
    def setUp(self):
        super().setUp()

        self.member = (
            Team.objects.create(
                name="Alice",
                position="Developer",
                image_png=image_upload(
                    "member.png"
                ),
            )
        )

    def test_delete_requires_csrf(
        self,
    ):
        self.login_admin()

        response = self.client.delete(
            self.delete_url(
                self.member
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_delete_member(
        self,
    ):
        self.login_admin()

        member_id = (
            self.member.pk
        )

        image_name = (
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
                self.client.delete(
                    self.delete_url(
                        self.member
                    ),
                    **self.csrf_headers(),
                )
            )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            Team.objects.filter(
                pk=member_id
            ).exists()
        )

        self.assertFalse(
            storage.exists(
                image_name
            )
        )