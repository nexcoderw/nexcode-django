from unittest.mock import patch

from django.db import transaction
from PIL import Image

from home.models import Team

from admin_api.tests.team.base import (
    TeamApiTestCase,
)
from admin_api.tests.team.files import (
    image_upload,
)


class TeamStorageTests(
    TeamApiTestCase
):
    def test_team_images_are_optimized_as_webp(
        self,
    ):
        member = Team.objects.create(
            name="Alice",
            position="Developer",
            image=image_upload(
                "portrait.png",
                size=(1600, 2000),
            ),
            image_png=image_upload(
                "cutout.png",
                size=(1600, 2000),
            ),
        )

        for field_name in (
            "image",
            "image_png",
        ):
            stored_file = getattr(
                member,
                field_name,
            )

            self.assertTrue(
                stored_file.name.endswith(
                    ".webp"
                )
            )

            with stored_file.storage.open(
                stored_file.name,
                "rb",
            ) as image_file:
                with Image.open(
                    image_file
                ) as processed_image:
                    self.assertEqual(
                        processed_image.format,
                        "WEBP",
                    )
                    self.assertEqual(
                        processed_image.size,
                        (800, 1000),
                    )

                    if field_name == "image_png":
                        self.assertIn(
                            "A",
                            processed_image.mode,
                        )

    def test_delete_uses_active_storage_backend(
        self,
    ):
        member = Team.objects.create(
            name="Alice",
            position="Developer",
            image_png=image_upload(
                "member.png"
            ),
        )

        storage = (
            member.image_png.storage
        )

        name = (
            member.image_png.name
        )

        with patch.object(
            storage,
            "delete",
            wraps=storage.delete,
        ) as delete_mock:
            with (
                self
                .captureOnCommitCallbacks(
                    execute=True
                )
            ):
                member.delete()

        delete_mock.assert_called_once_with(
            name
        )

    def test_rollback_does_not_delete_old_file(
        self,
    ):
        member = Team.objects.create(
            name="Alice",
            position="Developer",
            image_png=image_upload(
                "old.png"
            ),
        )

        storage = (
            member.image_png.storage
        )

        old_name = (
            member.image_png.name
        )

        with patch.object(
            storage,
            "delete",
            wraps=storage.delete,
        ) as delete_mock:
            try:
                with transaction.atomic():
                    member.image_png = (
                        image_upload(
                            "new.png"
                        )
                    )

                    member.save()

                    raise RuntimeError(
                        "Force rollback"
                    )
            except RuntimeError:
                pass

        self.assertTrue(
            storage.exists(
                old_name
            )
        )

        delete_mock.assert_not_called()
