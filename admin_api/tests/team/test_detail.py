from django.urls import reverse

from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)


class TeamDetailTests(
    TeamApiTestCase
):
    def setUp(self):
        super().setUp()

        self.member = (
            Team.objects.create(
                name="Alice",
                position="Developer",
            )
        )

    def test_admin_can_get_detail(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.detail_url(
                self.member
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        member = response.json()[
            "data"
        ]["team_member"]

        self.assertEqual(
            member["id"],
            self.member.pk,
        )

    def test_unknown_member_returns_404(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            reverse(
                "admin_api:team:detail",
                kwargs={
                    "team_id": 999999,
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
                self.member
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )