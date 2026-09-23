from home.models import PortfolioDocument

from admin_api.tests.portfolio.base import (
    PortfolioApiTestCase,
)


CONTRACT_URL = (
    "https://docs.nexcode.africa"
    "/contract"
)

ANALYSIS_URL = (
    "https://docs.nexcode.africa"
    "/system-analysis"
)


class PortfolioDocumentAddTests(
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
            self.document_add_url(
                self.portfolio
            ),
            {
                "title": "Contract",
                "url": CONTRACT_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertFalse(
            PortfolioDocument.objects
            .exists()
        )

    def test_add_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.post_json(
            self.document_add_url(
                self.portfolio
            ),
            {
                "title": "Contract",
                "url": CONTRACT_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_add_document(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.document_add_url(
                self.portfolio
            ),
            {
                "title": "Contract",
                "url": CONTRACT_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        document = response.json()[
            "data"
        ]["document"]

        self.assertEqual(
            document["title"],
            "Contract",
        )

        self.assertEqual(
            document["url"],
            CONTRACT_URL,
        )

    def test_duplicate_url_is_rejected(
        self,
    ):
        self.login_admin()

        PortfolioDocument.objects.create(
            portfolio=self.portfolio,
            title="Contract",
            url=CONTRACT_URL,
        )

        response = self.post_json(
            self.document_add_url(
                self.portfolio
            ),
            {
                "title": "Contract copy",
                "url": CONTRACT_URL,
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
            PortfolioDocument.objects
            .count(),
            1,
        )

    def test_same_url_on_another_portfolio_is_allowed(
        self,
    ):
        self.login_admin()

        PortfolioDocument.objects.create(
            portfolio=self.portfolio,
            title="Contract",
            url=CONTRACT_URL,
        )

        other = self.create_portfolio(
            name="Brand Refresh",
        )

        response = self.post_json(
            self.document_add_url(
                other
            ),
            {
                "title": "Contract",
                "url": CONTRACT_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_missing_fields_are_reported(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.document_add_url(
                self.portfolio
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        errors = response.json()[
            "errors"
        ]

        self.assertIn(
            "title",
            errors,
        )

        self.assertIn(
            "url",
            errors,
        )

    def test_invalid_url_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.document_add_url(
                self.portfolio
            ),
            {
                "title": "Contract",
                "url": "not-a-url",
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
        url = self.document_add_url(
            self.portfolio
        )

        self.portfolio.delete()

        response = self.post_json(
            url,
            {
                "title": "Contract",
                "url": CONTRACT_URL,
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
            self.document_add_url(
                self.portfolio
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioDocumentUpdateTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.document = (
            PortfolioDocument.objects
            .create(
                portfolio=(
                    self.portfolio
                ),
                title="Contract",
                url=CONTRACT_URL,
            )
        )

    def test_update_requires_authentication(
        self,
    ):
        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {
                "title": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_update_document(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {
                "title": "Signed contract",
                "url": ANALYSIS_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        document = response.json()[
            "data"
        ]["document"]

        self.assertEqual(
            document["title"],
            "Signed contract",
        )

        self.assertEqual(
            document["url"],
            ANALYSIS_URL,
        )

    def test_empty_payload_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_blank_title_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {
                "title": "",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "title",
            response.json()["errors"],
        )

    def test_duplicate_url_within_portfolio_is_rejected(
        self,
    ):
        self.login_admin()

        PortfolioDocument.objects.create(
            portfolio=self.portfolio,
            title="System analysis",
            url=ANALYSIS_URL,
        )

        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {
                "url": ANALYSIS_URL,
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

        # The uniqueness check must exclude the document being edited.
        response = self.patch_json(
            self.document_update_url(
                self.document.pk
            ),
            {
                "url": CONTRACT_URL,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_unknown_document_returns_404(
        self,
    ):
        self.login_admin()

        response = self.patch_json(
            self.document_update_url(
                999999
            ),
            {
                "title": "Renamed",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class PortfolioDocumentDeleteTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.document = (
            PortfolioDocument.objects
            .create(
                portfolio=(
                    self.portfolio
                ),
                title="Contract",
                url=CONTRACT_URL,
            )
        )

    def test_delete_requires_authentication(
        self,
    ):
        response = (
            self.delete_request(
                self.document_delete_url(
                    self.document.pk
                )
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertTrue(
            PortfolioDocument.objects
            .filter(
                pk=self.document.pk
            )
            .exists()
        )

    def test_admin_can_delete_document(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.document_delete_url(
                    self.document.pk
                )
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            PortfolioDocument.objects
            .filter(
                pk=self.document.pk
            )
            .exists()
        )

    def test_unknown_document_returns_404(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.document_delete_url(
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
            self.document_delete_url(
                self.document.pk
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
