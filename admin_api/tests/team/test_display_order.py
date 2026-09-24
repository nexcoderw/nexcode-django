from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)


class TeamDisplayOrderTests(
    TeamApiTestCase
):
    def add_member(
        self,
        **fields,
    ):
        data = {
            "name": "New Member",
            "position": "Engineer",
        }

        data.update(fields)

        return self.client.post(
            self.add_url,
            data=data,
            **self.csrf_headers(),
        )

    def names(
        self,
        response,
    ):
        return [
            item["name"]
            for item in response.json()[
                "data"
            ]["items"]
        ]

    def test_new_member_is_added_after_everyone_else(
        self,
    ):
        self.login_admin()

        Team.objects.create(
            name="Alice",
            position="Developer",
            display_order=4,
        )

        response = self.add_member()

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.json()["data"][
                "team_member"
            ]["display_order"],
            5,
        )

    def test_first_member_starts_at_one(
        self,
    ):
        self.login_admin()

        response = self.add_member()

        self.assertEqual(
            response.json()["data"][
                "team_member"
            ]["display_order"],
            1,
        )

    def test_explicit_order_is_kept_on_create(
        self,
    ):
        self.login_admin()

        response = self.add_member(
            display_order="2",
        )

        self.assertEqual(
            response.json()["data"][
                "team_member"
            ]["display_order"],
            2,
        )

    def test_order_can_be_changed(
        self,
    ):
        self.login_admin()

        member = Team.objects.create(
            name="Alice",
            position="Developer",
            display_order=1,
        )

        response = self.patch_multipart(
            self.update_url(member),
            {
                "display_order": "7",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        member.refresh_from_db()

        self.assertEqual(
            member.display_order,
            7,
        )

    def test_blank_order_on_update_keeps_the_position(
        self,
    ):
        self.login_admin()

        member = Team.objects.create(
            name="Alice",
            position="Developer",
            display_order=3,
        )

        response = self.patch_multipart(
            self.update_url(member),
            {
                "display_order": "",
                "position": "Lead Developer",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        member.refresh_from_db()

        self.assertEqual(
            member.display_order,
            3,
        )

    def test_negative_order_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.add_member(
            display_order="-1",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertFalse(
            Team.objects.exists()
        )

    def test_list_follows_display_order_by_default(
        self,
    ):
        self.login_admin()

        Team.objects.create(
            name="Charlie",
            position="Designer",
            display_order=1,
        )

        # Bob and Alice share a position; name breaks the tie.
        Team.objects.create(
            name="Bob",
            position="Engineer",
            display_order=2,
        )

        Team.objects.create(
            name="Alice",
            position="Engineer",
            display_order=2,
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            self.names(response),
            [
                "Charlie",
                "Alice",
                "Bob",
            ],
        )

    def test_public_order_matches_the_admin_order(
        self,
    ):
        Team.objects.create(
            name="Zed",
            position="Engineer",
            display_order=1,
        )

        Team.objects.create(
            name="Amy",
            position="Engineer",
            display_order=2,
        )

        # The public pages read Team's default ordering.
        self.assertEqual(
            list(
                Team.objects.values_list(
                    "name",
                    flat=True,
                )
            ),
            [
                "Zed",
                "Amy",
            ],
        )
