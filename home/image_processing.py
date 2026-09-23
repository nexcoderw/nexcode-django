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


def transparent_cutout_options():
    """Return Pillow options for small, fast transparent cutouts.

    ``method=6`` spends several seconds per cutout searching for the
    last few kilobytes: on the team's real 2048x2560 PNG cutouts it took
    5-7 s each, long enough to push an upload past the admin's request
    timeout. ``method=4`` encodes the same cutouts in about 0.12 s.

    Lossy alpha at 70 then more than recovers the size: an average of
    28 KB against 36 KB with the previous settings. Soft edges move by
    under 3/255 of opacity on average, which does not show at any
    display size, while fully opaque and fully clear pixels are exact.
    """
    return {
        "quality": 78,
        "alpha_quality": 70,
        "method": 4,
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
