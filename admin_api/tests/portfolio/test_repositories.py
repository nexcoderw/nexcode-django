from home.models import PortfolioRepository

from admin_api.tests.portfolio.base import (
    PortfolioApiTestCase,
)


API_REPOSITORY_URL = (
    "https://github.com/nexcode/api"
)

ADMIN_REPOSITORY_URL = (
    "https://github.com/nexcode/admin"
)


class PortfolioRepositoryAddTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

    def test_add_requires_authentication(
        self,
    ):
        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertFalse(
            PortfolioRepository.objects
            .exists()
        )

    def test_add_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_add_repository(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "label": "Backend",
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        repository = response.json()[
            "data"
        ]["repository"]

        self.assertEqual(
            repository["label"],
            "Backend",
        )

        self.assertEqual(
            repository["url"],
            API_REPOSITORY_URL,
        )

    def test_label_defaults_when_omitted(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.json()["data"][
                "repository"
            ]["label"],
            "Repository",
        )

    def test_duplicate_url_is_rejected(
        self,
    ):
        self.login_admin()

        PortfolioRepository.objects.create(
            portfolio=self.portfolio,
            label="Backend",
            url=API_REPOSITORY_URL,
        )

        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "label": "Backend copy",
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "url",
            response.json()["errors"],
        )

        self.assertEqual(
            PortfolioRepository.objects
            .count(),
            1,
        )

    def test_same_url_on_another_portfolio_is_allowed(
        self,
    ):
        self.login_admin()

        PortfolioRepository.objects.create(
            portfolio=self.portfolio,
            label="Backend",
            url=API_REPOSITORY_URL,
        )

        other = self.create_portfolio(
            name="Brand Refresh",
        )

        response = self.post_json(
            self.repository_add_url(
                other
            ),
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_missing_url_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.repository_add_url(
                self.portfolio
            ),
            {
                "label": "Backend",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "url",
            response.json()["errors"],
        )

    def test_unknown_portfolio_returns_404(
        self,
    ):
        self.login_admin()

        # The URL is built before the delete, because deleting an
        # instance clears its primary key.
        url = self.repository_add_url(
            self.portfolio
        )

        self.portfolio.delete()

        response = self.post_json(
            url,
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_add_rejects_get(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.repository_add_url(
                self.portfolio
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioRepositoryUpdateTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.repository = (
            PortfolioRepository.objects
            .create(
                portfolio=(
                    self.portfolio
                ),
                label="Backend",
                url=API_REPOSITORY_URL,
            )
        )

    def test_update_requires_authentication(
        self,
    ):
        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "label": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_update_repository(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "label": "Admin portal",
                "url": (
                    ADMIN_REPOSITORY_URL
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        repository = response.json()[
            "data"
        ]["repository"]

        self.assertEqual(
            repository["label"],
            "Admin portal",
        )

        self.assertEqual(
            repository["url"],
            ADMIN_REPOSITORY_URL,
        )

    def test_blank_label_falls_back_to_default(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "label": "",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["data"][
                "repository"
            ]["label"],
            "Repository",
        )

    def test_blank_url_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "url": "",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "url",
            response.json()["errors"],
        )

    def test_empty_payload_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_duplicate_url_within_portfolio_is_rejected(
        self,
    ):
        self.login_admin()

        PortfolioRepository.objects.create(
            portfolio=self.portfolio,
            label="Admin",
            url=ADMIN_REPOSITORY_URL,
        )

        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "url": (
                    ADMIN_REPOSITORY_URL
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "url",
            response.json()["errors"],
        )

    def test_unchanged_url_is_accepted(
        self,
    ):
        self.login_admin()

        # The uniqueness check must exclude the repository being edited.
        response = self.patch_json(
            self.repository_update_url(
                self.repository.pk
            ),
            {
                "url": API_REPOSITORY_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_unknown_repository_returns_404(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.repository_update_url(
                999999
            ),
            {
                "label": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class PortfolioRepositoryDeleteTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.repository = (
            PortfolioRepository.objects
            .create(
                portfolio=(
                    self.portfolio
                ),
                label="Backend",
                url=API_REPOSITORY_URL,
            )
        )

    def test_delete_requires_authentication(
        self,
    ):
        response = (
            self.delete_request(
                self.repository_delete_url(
                    self.repository.pk
                )
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertTrue(
            PortfolioRepository.objects
            .filter(
                pk=self.repository.pk
            )
            .exists()
        )

    def test_admin_can_delete_repository(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.repository_delete_url(
                    self.repository.pk
                )
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            PortfolioRepository.objects
            .filter(
                pk=self.repository.pk
            )
            .exists()
        )

    def test_unknown_repository_returns_404(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.repository_delete_url(
                    999999
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
            self.repository_delete_url(
                self.repository.pk
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
