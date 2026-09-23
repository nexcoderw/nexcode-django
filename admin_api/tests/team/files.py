from io import BytesIO

from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from PIL import Image


def image_upload(
    filename="member.png",
    image_format="PNG",
    size=(40, 40),
    transparent=False,
):
    """Build an in-memory image upload.

    With ``transparent`` set, the PNG is a cutout: a clear canvas with an
    opaque subject in the middle. A solid fill is not enough to test
    transparency, because WebP encoders drop an alpha channel whose
    pixels are all fully opaque.
    """
    buffer = BytesIO()

    mode = (
        "RGBA"
        if image_format == "PNG"
        else "RGB"
    )

    if transparent and mode == "RGBA":
        image = Image.new(
            mode,
            size,
            (0, 0, 0, 0),
        )

        width, height = size

        image.paste(
            (255, 0, 0, 255),
            (
                width // 4,
                height // 4,
                width * 3 // 4,
                height * 3 // 4,
            ),
        )
    else:
        image = Image.new(
            mode,
            size,
            (
                (255, 0, 0, 255)
                if mode == "RGBA"
                else (255, 0, 0)
            ),
        )

    image.save(
        buffer,
        format=image_format,
    )

    content_types = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }

    return SimpleUploadedFile(
        filename,
        buffer.getvalue(),
        content_type=(
            content_types[
                image_format
            ]
        ),
    )


def oversized_jpeg_upload():
    image = image_upload(
        "large.jpg",
        "JPEG",
    )

    data = (
        image.read()
        + b"\0"
        * (
            10 * 1024 * 1024
            + 1
        )
    )

    return SimpleUploadedFile(
        "large.jpg",
        data,
        content_type="image/jpeg",
    )
