from uuid import uuid4

from django.utils.text import slugify


def team_image_path(
    instance,
    filename,
):
    member = _member_slug(
        instance
    )

    return (
        "team/images/"
        f"{member}/"
        f"{uuid4().hex}.jpg"
    )


def team_png_image_path(
    instance,
    filename,
):
    member = _member_slug(
        instance
    )

    return (
        "team/cutouts/"
        f"{member}/"
        f"{uuid4().hex}.png"
    )


def _member_slug(instance):
    return (
        slugify(
            instance.name or ""
        )
        or "team-member"
    )