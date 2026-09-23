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
    PortfolioDocument,
    PortfolioImage,
)


class PortfolioStorageTests(
    TestCase
):
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

        self.document_field = (
            PortfolioDocument
            ._meta
            .get_field("file")
        )

        self.original_image_storage = (
            self.image_field.storage
        )

        self.original_document_storage = (
            self.document_field.storage
        )

        self.image_field.storage = (
            self.storage
        )

        self.document_field.storage = (
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

        self.document_field.storage = (
            self.original_document_storage
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
                        "profile.png"
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
                ".jpg"
            )
        )

    def test_document_uses_structured_directory(
        self,
    ):
        document = (
            PortfolioDocument.objects.create(
                portfolio=(
                    self.portfolio
                ),
                title="Contract",
                document_type=(
                    PortfolioDocument
                    .DocumentType
                    .CONTRACT
                ),
                file=(
                    document_upload(
                        "contract.pdf"
                    )
                ),
            )
        )

        self.assertTrue(
            document.file.name.startswith(
                "portfolios/"
                "storage-test/"
                "documents/"
                "contract/"
            )
        )

        self.assertTrue(
            document.file.name.endswith(
                ".pdf"
            )
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

        document = (
            PortfolioDocument.objects.create(
                portfolio=(
                    self.portfolio
                ),
                title="Analysis",
                document_type=(
                    PortfolioDocument
                    .DocumentType
                    .SYSTEM_ANALYSIS
                ),
                file=(
                    document_upload(
                        "analysis.pdf"
                    )
                ),
            )
        )

        image_name = (
            image.image.name
        )

        document_name = (
            document.file.name
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

        self.assertFalse(
            self.storage.exists(
                document_name
            )
        )


def image_upload(
    filename,
):
    buffer = BytesIO()

    Image.new(
        "RGB",
        (100, 100),
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


def document_upload(
    filename,
):
    return SimpleUploadedFile(
        filename,
        b"%PDF-1.4 test document",
        content_type="application/pdf",
    )