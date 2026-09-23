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

from home.models import Client


class ClientStorageTests(
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
            Client
            ._meta
            .get_field(
                "profile_image"
            )
        )

        self.original_image_storage = (
            self.image_field.storage
        )

        self.image_field.storage = (
            self.storage
        )

    def tearDown(self):
        self.image_field.storage = (
            self.original_image_storage
        )

        self.media_directory.cleanup()

    def test_profile_image_uses_client_directory(
        self,
    ):
        client = (
            Client.objects.create(
                name="Storage Client",
                profile_image=(
                    image_upload(
                        "profile.png"
                    )
                ),
            )
        )

        self.assertTrue(
            client.profile_image.name
            .startswith(
                "clients/profiles/"
                "storage-client/"
            )
        )

        self.assertTrue(
            client.profile_image.name
            .endswith(
                ".jpg"
            )
        )

    def test_replacing_profile_image_deletes_old_file_after_commit(
        self,
    ):
        client = (
            Client.objects.create(
                name="Storage Client",
                profile_image=(
                    image_upload(
                        "old.png"
                    )
                ),
            )
        )

        old_name = (
            client.profile_image.name
        )

        self.assertTrue(
            self.storage.exists(
                old_name
            )
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            client.profile_image = (
                image_upload(
                    "new.png"
                )
            )

            client.save()

        self.assertFalse(
            self.storage.exists(
                old_name
            )
        )

        self.assertTrue(
            self.storage.exists(
                client.profile_image.name
            )
        )

    def test_deleting_client_cleans_profile_image(
        self,
    ):
        client = (
            Client.objects.create(
                name="Storage Client",
                profile_image=(
                    image_upload(
                        "profile.png"
                    )
                ),
            )
        )

        image_name = (
            client.profile_image.name
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            client.delete()

        self.assertFalse(
            self.storage.exists(
                image_name
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