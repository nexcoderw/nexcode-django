import re
from pathlib import Path
from uuid import uuid4

from django.utils.text import slugify


def team_image_path(
    instance,
    filename,
):
    member = _team_slug(
        instance
    )

    return (
        "team/images/"
        f"{member}/"
        f"{uuid4().hex}.webp"
    )


def team_png_image_path(
    instance,
    filename,
):
    member = _team_slug(
        instance
    )

    return (
        "team/cutouts/"
        f"{member}/"
        f"{uuid4().hex}.webp"
    )


def portfolio_gallery_image_path(
    instance,
    filename,
):
    portfolio = _portfolio_slug(
        instance.portfolio
    )

    return (
        "portfolios/"
        f"{portfolio}/"
        "images/"
        f"{uuid4().hex}.webp"
    )


def portfolio_document_path(
    instance,
    filename,
):
    portfolio = _portfolio_slug(
        instance.portfolio
    )

    document_type = (
        slugify(
            instance.document_type
            or ""
        )
        or "other"
    )

    extension = (
        _safe_extension(
            filename
        )
    )

    return (
        "portfolios/"
        f"{portfolio}/"
        "documents/"
        f"{document_type}/"
        f"{uuid4().hex}"
        f"{extension}"
    )


def _team_slug(instance):
    return (
        slugify(
            instance.name or ""
        )
        or "team-member"
    )


def client_profile_image_path(
    instance,
    filename,
):
    """Retired upload path, kept only so migration 0035 still imports.

    Clients no longer store a profile image, so nothing calls this. It
    must stay defined for as long as that historical migration exists;
    removing it would break every migrate and test run.
    """
    return (
        "clients/profiles/"
        f"{uuid4().hex}.webp"
    )

def _portfolio_slug(
    portfolio,
):
    return (
        portfolio.slug
        or slugify(
            portfolio.name or ""
        )
        or "portfolio"
    )


def _safe_extension(
    filename,
):
    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    if not re.fullmatch(
        r"\.[a-z0-9]{1,10}",
        extension,
    ):
        return ""

    return extension
