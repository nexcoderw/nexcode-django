from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import (
    Client,
    TestCase,
)
from django.urls import reverse

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from home.models import Team


class AdminTeamApiTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.group, _ = (
            Group.objects.get_or_create(
                name=(
                    NEXCODE_ADMIN_GROUP_NAME
                ),
            )
        )

        self.admin_user = (
            User.objects.create_user(
                username=(
                    "admin@nexcode.africa"
                ),
                email=(
                    "admin@nexcode.africa"
                ),
                password=(
                    "TestPassword123!"
                ),
            )
        )

        self.admin_user.groups.add(
            self.group
        )

        self.regular_user = (
            User.objects.create_user(
                username=(
                    "user@nexcode.africa"
                ),
                email=(
                    "user@nexcode.africa"
                ),
                password=(
                    "TestPassword123!"
                ),
            )
        )

        self.member_one = (
            Team.objects.create(
                name="Alice Developer",
                slug="alice-developer",
                position=(
                    "Software Engineer"
                ),
                github=(
                    "https://github.com/alice"
                ),
            )
        )

        self.member_two = (
            Team.objects.create(
                name="Bob Designer",
                slug="bob-designer",
                position=(
                    "Product Designer"
                ),
                linkedin=(
                    "https://linkedin.com/in/bob"
                ),
            )
        )

        self.client = Client()

        self.list_url = reverse(
            "admin_api:team:list"
        )

    def detail_url(
        self,
        team_member,
    ):
        return reverse(
            "admin_api:team:detail",
            kwargs={
                "team_id":
                    team_member.pk,
            },
        )

    def test_team_list_requires_authentication(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_team_list_rejects_non_admin_user(
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

    def test_admin_can_list_team_members(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

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

        self.assertEqual(
            len(data["items"]),
            2,
        )

    def test_team_list_can_search(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "designer",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
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

    def test_team_list_can_order_by_name(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

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

    def test_team_list_rejects_invalid_ordering(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            self.list_url,
            {
                "ordering":
                    "invalid_field",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_team_list_rejects_invalid_page_size(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

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

    def test_admin_can_get_team_member_detail(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            self.detail_url(
                self.member_one
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
            self.member_one.pk,
        )

        self.assertEqual(
            member["name"],
            "Alice Developer",
        )

        self.assertEqual(
            member["position"],
            "Software Engineer",
        )

    def test_team_detail_returns_404_for_unknown_member(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

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

    def test_team_endpoints_do_not_allow_post(
        self,
    ):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.post(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            405,
        )