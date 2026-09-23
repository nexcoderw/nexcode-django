from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)

from home.models import PortfolioImage

from admin_api.tests.portfolio.base import (
    PortfolioApiTestCase,
)

# The portfolio gallery accepts the same formats and size ceiling as the
# team profile images, so the existing upload builders are reused rather
# than duplicated.
from admin_api.tests.team.files import (
    image_upload,
    oversized_jpeg_upload,
)


class PortfolioImageAddTests(
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
        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image":
                        image_upload(),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertFalse(
            PortfolioImage.objects
            .exists()
        )

    def test_add_rejects_non_admin(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image":
                        image_upload(),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_add_image(
        self,
    ):
        self.login_admin()

        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image":
                        image_upload(),
                    "alt_text":
                        "Dashboard view",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        image = response.json()[
            "data"
        ]["image"]

        self.assertEqual(
            image["alt_text"],
            "Dashboard view",
        )

        self.assertFalse(
            image["is_cover"]
        )

        self.assertEqual(
            image["position"],
            0,
        )

        self.assertIsNotNone(
            image["image"]
        )

    def test_position_increments_by_default(
        self,
    ):
        self.login_admin()

        for _ in range(2):
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image":
                        image_upload(),
                },
            )

        positions = list(
            PortfolioImage.objects
            .filter(
                portfolio=(
                    self.portfolio
                )
            )
            .order_by("pk")
            .values_list(
                "position",
                flat=True,
            )
        )

        self.assertEqual(
            positions,
            [0, 1],
        )

    def test_new_cover_replaces_previous_cover(
        self,
    ):
        self.login_admin()

        first = self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
                "is_cover": "true",
            },
        )

        self.assertEqual(
            first.status_code,
            201,
        )

        second = self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
                "is_cover": "true",
            },
        )

        self.assertEqual(
            second.status_code,
            201,
        )

        covers = list(
            PortfolioImage.objects
            .filter(
                portfolio=(
                    self.portfolio
                ),
                is_cover=True,
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            covers,
            [
                second.json()["data"][
                    "image"
                ]["id"],
            ],
        )

    def test_cover_image_appears_in_list(
        self,
    ):
        self.login_admin()

        self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
                "is_cover": "true",
            },
        )

        response = self.client.get(
            self.list_url
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertIsNotNone(
            items[0]["cover_image"]
        )

    def test_non_image_file_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image": (
                        SimpleUploadedFile(
                            "notes.txt",
                            b"not an image",
                            content_type=(
                                "text/plain"
                            ),
                        )
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "image",
            response.json()["errors"],
        )

    def test_oversized_image_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "image": (
                        oversized_jpeg_upload()
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertFalse(
            PortfolioImage.objects
            .exists()
        )

    def test_missing_image_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.post_multipart(
                self.image_add_url(
                    self.portfolio
                ),
                {
                    "alt_text": "Only text",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_json_request_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.image_add_url(
                self.portfolio
            ),
            {
                "alt_text": "No file",
            },
        )

        self.assertEqual(
            response.status_code,
            415,
        )

    def test_unknown_portfolio_returns_404(
        self,
    ):
        self.login_admin()

        # The URL is built before the delete, because deleting an
        # instance clears its primary key.
        url = self.image_add_url(
            self.portfolio
        )

        self.portfolio.delete()

        response = (
            self.post_multipart(
                url,
                {
                    "image":
                        image_upload(),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class PortfolioImageUpdateTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.login_admin()

        created = self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
                "alt_text": "Original",
            },
        )

        self.image_id = (
            created.json()["data"][
                "image"
            ]["id"]
        )

        self.client.logout()

    def test_update_requires_authentication(
        self,
    ):
        response = (
            self.patch_multipart(
                self.image_update_url(
                    self.image_id
                ),
                {
                    "alt_text": "Changed",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_admin_can_update_alt_text(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.image_update_url(
                    self.image_id
                ),
                {
                    "alt_text": "Changed",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["data"][
                "image"
            ]["alt_text"],
            "Changed",
        )

    def test_promoting_cover_demotes_others(
        self,
    ):
        self.login_admin()

        other = self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
                "is_cover": "true",
            },
        )

        other_id = other.json()[
            "data"
        ]["image"]["id"]

        response = (
            self.patch_multipart(
                self.image_update_url(
                    self.image_id
                ),
                {
                    "is_cover": "true",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            PortfolioImage.objects.get(
                pk=other_id
            ).is_cover
        )

        self.assertTrue(
            PortfolioImage.objects.get(
                pk=self.image_id
            ).is_cover
        )

    def test_empty_update_is_rejected(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.image_update_url(
                    self.image_id
                ),
                {},
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_unknown_image_returns_404(
        self,
    ):
        self.login_admin()

        response = (
            self.patch_multipart(
                self.image_update_url(
                    999999
                ),
                {
                    "alt_text": "Changed",
                },
            )
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
            self.image_update_url(
                self.image_id
            ),
            **self.csrf_headers(),
        )

        self.assertEqual(
            response.status_code,
            405,
        )


class PortfolioImageDeleteTests(
    PortfolioApiTestCase
):
    def setUp(self):
        super().setUp()

        self.portfolio = (
            self.create_portfolio()
        )

        self.login_admin()

        created = self.post_multipart(
            self.image_add_url(
                self.portfolio
            ),
            {
                "image": image_upload(),
            },
        )

        self.image_id = (
            created.json()["data"][
                "image"
            ]["id"]
        )

        self.client.logout()

    def test_delete_requires_authentication(
        self,
    ):
        response = (
            self.delete_request(
                self.image_delete_url(
                    self.image_id
                )
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertTrue(
            PortfolioImage.objects
            .filter(
                pk=self.image_id
            )
            .exists()
        )

    def test_admin_can_delete_image(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.image_delete_url(
                    self.image_id
                )
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            PortfolioImage.objects
            .filter(
                pk=self.image_id
            )
            .exists()
        )

    def test_unknown_image_returns_404(
        self,
    ):
        self.login_admin()

        response = (
            self.delete_request(
                self.image_delete_url(
                    999999
                )
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
