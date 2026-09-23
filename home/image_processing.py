from imagekit.processors import (
    ResizeToFill,
    ResizeToFit,
)


WEB_IMAGE_FORMAT = "WEBP"
WEB_IMAGE_QUALITY = 82


def web_image_options():
    """Return Pillow options for compact, high-quality WebP output."""
    return {
        "quality": WEB_IMAGE_QUALITY,
        "method": 6,
    }


def portrait_processors():
    """Crop a portrait to the dimensions used by profile interfaces."""
    return [
        ResizeToFill(
            800,
            1000,
            upscale=False,
        ),
    ]


def square_profile_processors():
    """Crop a profile image to a compact square."""
    return [
        ResizeToFill(
            800,
            800,
            upscale=False,
        ),
    ]


def transparent_cutout_processors():
    """Fit a transparent cutout without cropping or enlarging it."""
    return [
        ResizeToFit(
            800,
            1000,
            upscale=False,
        ),
    ]


def portfolio_image_processors():
    """Crop gallery imagery to its responsive display aspect ratio."""
    return [
        ResizeToFill(
            1280,
            900,
            upscale=False,
        ),
    ]
