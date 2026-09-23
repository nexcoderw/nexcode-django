from datetime import date

from django.urls import reverse

from home.models import (
    Portfolio,
    PortfolioDocument,
    PortfolioRepository,
    Team,
)

from admin_api.tests.portfolio.base import (
    PortfolioApiTestCase,
)


class PortfolioCreateTests(
    PortfolioApiTestCase
):
    def payload(
        self,
        **overrides,
    ):
        data = {
            "name": "NEXCODE Platform",
            "summary": (
                "Internal operations "
                "portal."
            ),
            "category": (
                Portfolio.Category
                .WEB_APPLICATION
            ),
            "project_type": (
                Portfolio.ProjectType
                .CLIENT_PROJECT
            ),
        }

        data.update(overrides)

        return data

    def test_create_requires_authentication(
        self,
    ):
        response = self.post_json(
            self.add_url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertFalse(
            Portfolio.objects.exists()
        )

    def test_create_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.post_json(
            self.add_url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_create_portfolio(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                live_url=(
                    "https://nexcode.africa"
                ),
            ),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        portfolio = (
            response.json()["data"][
                "portfolio"
            ]
        )

        self.assertEqual(
            portfolio["name"],
            "NEXCODE Platform",
        )

        # Draft is the documented default when no status is sent.
        self.assertEqual(
            portfolio["status"],
            Portfolio.Status.DRAFT,
        )

        self.assertIsNone(
            portfolio["published_at"]
        )

        self.assertTrue(
            portfolio["slug"]
        )

    def test_publishing_sets_published_at(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                status=(
                    Portfolio.Status
                    .PUBLISHED
                ),
            ),
        )

        portfolio = (
            response.json()["data"][
                "portfolio"
            ]
        )

        self.assertIsNotNone(
            portfolio["published_at"]
        )

    def test_create_attaches_team_members(
        self,
    ):
        self.login_admin()

        member = (
            Team.objects.create(
                name="Alice Developer",
                position=(
                    "Software Engineer"
                ),
            )
        )

        response = self.post_json(
            self.add_url,
            self.payload(
                team_member_ids=[
                    member.pk,
                ],
            ),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        members = (
            response.json()["data"][
                "portfolio"
            ]["team_members"]
        )

        self.assertEqual(
            [
                entry["id"]
                for entry in members
            ],
            [member.pk],
        )

    def test_missing_required_fields_are_reported(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            {
                "summary": "No name.",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        errors = response.json()[
            "errors"
        ]

        self.assertIn(
            "name",
            errors,
        )

        self.assertIn(
            "category",
            errors,
        )

        self.assertIn(
            "project_type",
            errors,
        )

    def test_invalid_category_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                category="unknown",
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "category",
            response.json()["errors"],
        )

    def test_deadline_before_start_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.add_url,
            self.payload(
                project_initiation_date=(
                    "2026-03-01"
                ),
                deadline_date=(
                    "2026-01-01"
                ),
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "deadline_date",
            response.json()["errors"],
        )

        self.assertFalse(
            Portfolio.objects.exists()
        )

    def test_non_json_request_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            data={
                "name": "Plain form",
            },
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            415,
        )

    def test_invalid_json_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.add_url,
            data="{not json",
            content_type=(
                "application/json"
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_create_rejects_get(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.add_url
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioDetailTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

    def test_detail_requires_authentication(
        self,
    ):
        response = self.client.get(
            self.detail_url(
                self.portfolio
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_read_detail(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.detail_url(
                self.portfolio
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        portfolio = (
            response.json()["data"][
                "portfolio"
            ]
        )

        self.assertEqual(
            portfolio["id"],
            self.portfolio.pk,
        )

        for collection in (
            "team_members",
            "images",
            "documents",
            "repositories",
        ):
            self.assertEqual(
                portfolio[collection],
                [],
            )

    def test_unknown_portfolio_returns_404(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            reverse(
                (
                    "admin_api:portfolio"
                    ":detail"
                ),
                kwargs={
                    "portfolio_id":
                        999999,
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
                self.portfolio
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioUpdateTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio(
                summary="Original.",
                project_initiation_date=(
                    date(2026, 2, 1)
                ),
            )
        )

    def test_update_requires_authentication(
        self,
    ):
        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "name": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_update_fields(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "name": "Renamed",
                "summary": "Updated.",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        portfolio = (
            response.json()["data"][
                "portfolio"
            ]
        )

        self.assertEqual(
            portfolio["name"],
            "Renamed",
        )

        self.assertEqual(
            portfolio["summary"],
            "Updated.",
        )

        self.portfolio.refresh_from_db()

        self.assertEqual(
            self.portfolio.name,
            "Renamed",
        )

    def test_untouched_fields_are_preserved(
        self,
    ):
        self.login_admin()

        self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "name": "Renamed",
            },
        )

        self.portfolio.refresh_from_db()

        self.assertEqual(
            self.portfolio.summary,
            "Original.",
        )

    def test_empty_payload_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_blank_name_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "name": "",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "name",
            response.json()["errors"],
        )

    def test_deadline_is_validated_against_stored_start(
        self,
    ):
        self.login_admin()

        # Only the deadline is sent: the start date must still be read
        # from the stored portfolio for the comparison to mean anything.
        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "deadline_date":
                    "2026-01-01",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "deadline_date",
            response.json()["errors"],
        )

    def test_team_members_can_be_replaced(
        self,
    ):
        self.login_admin()

        first = Team.objects.create(
            name="Alice Developer",
            position="Engineer",
        )

        second = Team.objects.create(
            name="Bob Designer",
            position="Designer",
        )

        self.portfolio.team_members.add(
            first
        )

        response = self.patch_json(
            self.update_url(
                self.portfolio
            ),
            {
                "team_member_ids": [
                    second.pk,
                ],
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        members = (
            response.json()["data"][
                "portfolio"
            ]["team_members"]
        )

        self.assertEqual(
            [
                entry["id"]
                for entry in members
            ],
            [second.pk],
        )

    def test_unknown_portfolio_returns_404(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            reverse(
                (
                    "admin_api:portfolio"
                    ":update"
                ),
                kwargs={
                    "portfolio_id":
                        999999,
                },
            ),
            {
                "name": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_rejects_post(
        self,
    ):
        self.login_admin()

        response = self.client.post(
            self.update_url(
                self.portfolio
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioDeleteTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

    def test_delete_requires_authentication(
        self,
    ):
        response = (
            self.delete_request(
                self.delete_url(
                    self.portfolio
                )
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertTrue(
            Portfolio.objects.filter(
                pk=self.portfolio.pk
            ).exists()
        )

    def test_delete_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = (
            self.delete_request(
                self.delete_url(
                    self.portfolio
                )
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_delete_portfolio(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.delete_url(
                    self.portfolio
                )
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            Portfolio.objects.filter(
                pk=self.portfolio.pk
            ).exists()
        )

    def test_delete_removes_related_records(
        self,
    ):
        self.login_admin()

        PortfolioDocument.objects.create(
            portfolio=self.portfolio,
            title="Contract",
            url=(
                "https://docs.nexcode"
                ".africa/contract"
            ),
        )

        PortfolioRepository.objects.create(
            portfolio=self.portfolio,
            label="API",
            url=(
                "https://github.com"
                "/nexcode/api"
            ),
        )

        self.delete_request(
            self.delete_url(
                self.portfolio
            )
        )

        self.assertFalse(
            PortfolioDocument.objects
            .exists()
        )

        self.assertFalse(
            PortfolioRepository.objects
            .exists()
        )

    def test_unknown_portfolio_returns_404(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                reverse(
                    (
                        "admin_api"
                        ":portfolio:delete"
                    ),
                    kwargs={
                        "portfolio_id":
                            999999,
                    },
                )
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
                self.portfolio
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
