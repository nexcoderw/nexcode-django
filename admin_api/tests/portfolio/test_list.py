from home.models import (
    Portfolio,
    Team,
)

from admin_api.tests.portfolio.base import (
    PortfolioApiTestCase,
)


class PortfolioListTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.designer = (
            Team.objects.create(
                name="Bob Designer",
                position=(
                    "Product Designer"
                ),
            )
        )

        self.platform = (
            self.create_portfolio(
                name="NEXCODE Platform",
                summary=(
                    "Internal operations "
                    "portal."
                ),
                status=(
                    Portfolio.Status
                    .PUBLISHED
                ),
            )
        )

        self.platform.team_members.add(
            self.designer
        )

        self.brand = (
            self.create_portfolio(
                name="Brand Refresh",
                summary=(
                    "Identity and "
                    "guidelines."
                ),
                category=(
                    Portfolio.Category
                    .BRANDING
                ),
                project_type=(
                    Portfolio.ProjectType
                    .STUDENT_PROJECT
                ),
            )
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

    def test_admin_can_list_portfolios(
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

        self.assertEqual(
            data["pagination"][
                "page_size"
            ],
            20,
        )

    def test_summary_counts_team_members(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "Platform",
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
            items[0][
                "team_member_count"
            ],
            1,
        )

        # No cover image has been uploaded for this portfolio.
        self.assertIsNone(
            items[0]["cover_image"]
        )

    def test_search_matches_summary(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "identity",
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
            ["Brand Refresh"],
        )

    def test_category_filter(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "category": (
                    Portfolio.Category
                    .BRANDING
                ),
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
            ["Brand Refresh"],
        )

    def test_project_type_filter(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "project_type": (
                    Portfolio.ProjectType
                    .STUDENT_PROJECT
                ),
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
            ["Brand Refresh"],
        )

    def test_status_filter(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "status": (
                    Portfolio.Status
                    .PUBLISHED
                ),
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
            ["NEXCODE Platform"],
        )

    def test_team_member_filter(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "team_member_id": (
                    self.designer.pk
                ),
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
            ["NEXCODE Platform"],
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
                "Brand Refresh",
                "NEXCODE Platform",
            ],
        )

    def test_invalid_ordering_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering": (
                    "name; DROP TABLE"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_category_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "category": "unknown",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_team_member_id_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "team_member_id": "abc",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_page_size_limit_is_enforced(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "page_size": "500",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_pagination_reports_pages(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "page_size": "1",
            },
        )

        pagination = (
            response.json()["data"][
                "pagination"
            ]
        )

        self.assertEqual(
            pagination["total_pages"],
            2,
        )

        self.assertTrue(
            pagination["has_next"]
        )

        self.assertFalse(
            pagination[
                "has_previous"
            ]
        )

    def test_list_rejects_post(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.list_url,
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )

        self.assertEqual(
            response["Allow"],
            "GET",
        )
