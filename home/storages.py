from django.conf import settings
from django.core.files.storage import (
    FileSystemStorage,
)


def raw_media_storage():
    if (
        settings.DJANGO_ENV
        == "production"
    ):
        from cloudinary_storage.storage import (
            RawMediaCloudinaryStorage,
        )

        return (
            RawMediaCloudinaryStorage()
        )

    return FileSystemStorage(
        location=settings.MEDIA_ROOT,
        base_url=settings.MEDIA_URL,
    )