from io import BytesIO

from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from PIL import Image


def image_upload(
    filename="client.png",
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