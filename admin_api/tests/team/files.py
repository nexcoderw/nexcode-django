from io import BytesIO

from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from PIL import Image


def image_upload(
    filename="member.png",
    image_format="PNG",
    size=(40, 40),
):
    buffer = BytesIO()

    mode = (
        "RGBA"
        if image_format == "PNG"
        else "RGB"
    )

    Image.new(
        mode,
        size,
        (
            (255, 0, 0, 255)
            if mode == "RGBA"
            else (255, 0, 0)
        ),
    ).save(
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
