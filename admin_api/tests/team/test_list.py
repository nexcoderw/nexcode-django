from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)


class TeamListTests(
    TeamApiTestCase
):
    def setUp(self):
        super().setUp()

        Team.objects.create(
            name="Alice Developer",
            position=(
                "Software Engineer"
            ),
        )

        Team.objects.create(
            name="Bob Designer",
            position=(
                "Product Designer"
            ),
        )

    def test_list_requires_authentication(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_list_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_list_team(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()[
            "data"
        ]

        self.assertEqual(
            data["pagination"][
                "total_items"
            ],
            2,
        )

    def test_search_filters_team(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "designer",
            },
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            len(items),
            1,
        )

        self.assertEqual(
            items[0]["name"],
            "Bob Designer",
        )

    def test_ordering_is_supported(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering": "name",
            },
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            [
                item["name"]
                for item in items
            ],
            [
                "Alice Developer",
                "Bob Designer",
            ],
        )

    def test_invalid_ordering_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering":
                    "secret_field",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_page_size_is_bounded(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "page_size": 101,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )