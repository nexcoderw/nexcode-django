import tempfile
from io import BytesIO

from django.core.files.storage import (
    FileSystemStorage,
)
from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.test import TestCase
from PIL import Image

from home.models import (
    Portfolio,
    PortfolioImage,
)


class PortfolioStorageTests(
    TestCase
):
    """Storage behaviour for portfolio gallery images.

    Portfolio documents are stored as links rather than uploads, so the
    only portfolio files on disk are gallery images.
    """

    def setUp(self):
        self.media_directory = (
            tempfile.TemporaryDirectory()
        )

        self.storage = (
            FileSystemStorage(
                location=(
                    self.media_directory
                    .name
                ),
                base_url="/media/",
            )
        )

        self.image_field = (
            PortfolioImage
            ._meta
            .get_field("image")
        )

        self.original_image_storage = (
            self.image_field.storage
        )

        self.image_field.storage = (
            self.storage
        )

        self.portfolio = (
            Portfolio.objects.create(
                name="Storage Test",
                category=(
                    Portfolio.Category
                    .WEB_APPLICATION
                ),
                project_type=(
                    Portfolio.ProjectType
                    .CLIENT_PROJECT
                ),
            )
        )

    def tearDown(self):
        self.image_field.storage = (
            self.original_image_storage
        )

        self.media_directory.cleanup()

    def test_image_uses_portfolio_directory(
        self,
    ):
        image = (
            PortfolioImage.objects.create(
                portfolio=(
                    self.portfolio
                ),
                image=(
                    image_upload(
                        "profile.png",
                        size=(1600, 1200),
                    )
                ),
            )
        )

        self.assertTrue(
            image.image.name.startswith(
                "portfolios/"
                "storage-test/"
                "images/"
            )
        )

        self.assertTrue(
            image.image.name.endswith(
                ".webp"
            )
        )

        with self.storage.open(
            image.image.name,
            "rb",
        ) as stored_image:
            with Image.open(
                stored_image
            ) as processed_image:
                self.assertEqual(
                    processed_image.format,
                    "WEBP",
                )
                self.assertEqual(
                    processed_image.size,
                    (1280, 900),
                )

    def test_replacing_image_deletes_old_file_after_commit(
        self,
    ):
        image = (
            PortfolioImage.objects.create(
                portfolio=(
                    self.portfolio
                ),
                image=(
                    image_upload(
                        "old.png"
                    )
                ),
            )
        )

        old_name = image.image.name

        self.assertTrue(
            self.storage.exists(
                old_name
            )
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            image.image = (
                image_upload(
                    "new.png"
                )
            )

            image.save()

        self.assertFalse(
            self.storage.exists(
                old_name
            )
        )

        self.assertTrue(
            self.storage.exists(
                image.image.name
            )
        )

    def test_deleting_portfolio_cleans_related_files(
        self,
    ):
        image = (
            PortfolioImage.objects.create(
                portfolio=(
                    self.portfolio
                ),
                image=(
                    image_upload(
                        "image.png"
                    )
                ),
            )
        )

        image_name = (
            image.image.name
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            self.portfolio.delete()

        self.assertFalse(
            self.storage.exists(
                image_name
            )
        )


def image_upload(
    filename,
    size=(100, 100),
):
    buffer = BytesIO()

    Image.new(
        "RGB",
        size,
        (255, 255, 255),
    ).save(
        buffer,
        format="PNG",
    )

    return SimpleUploadedFile(
        filename,
        buffer.getvalue(),
        content_type="image/png",
    )
