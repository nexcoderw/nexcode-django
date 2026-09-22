from pathlib import Path
from uuid import uuid4

from django.utils.text import slugify


def client_image_path(
    instance,
    filename,
):
    return _image_path(
        "clients/profiles",
        instance.name,
        ".jpg",
    )


def portfolio_image_path(
    instance,
    filename,
):
    name = getattr(
        instance,
        "name",
        None,
    )

    if not name:
        portfolio = getattr(
            instance,
            "portfolio",
            None,
        )

        name = getattr(
            portfolio,
            "name",
            None,
        )

    return _image_path(
        "portfolios/images",
        name,
        ".jpg",
    )


def team_image_path(
    instance,
    filename,
):
    return _image_path(
        "team/profiles",
        instance.name,
        ".jpg",
    )


def team_png_image_path(
    instance,
    filename,
):
    return _image_path(
        "team/cutouts",
        instance.name,
        ".png",
    )


def logo_image_path(
    instance,
    filename,
):
    return (
        "settings/branding/"
        f"{uuid4().hex}.png"
    )


def blog_image_path(
    instance,
    filename,
):
    return _image_path(
        "blogs/featured",
        instance.title,
        ".jpg",
    )


def training_image_path(
    instance,
    filename,
):
    return _image_path(
        "trainings/images",
        instance.title,
        ".jpg",
    )


def portfolio_system_analysis_path(
    instance,
    filename,
):
    return _document_path(
        "portfolios/documents/"
        "system-analysis",
        instance.name,
        filename,
    )


def portfolio_contract_path(
    instance,
    filename,
):
    return _document_path(
        "portfolios/documents/"
        "contracts",
        instance.name,
        filename,
    )


def _image_path(
    root,
    label,
    extension,
):
    folder = _safe_slug(
        label,
        "item",
    )

    return (
        f"{root}/"
        f"{folder}/"
        f"{uuid4().hex}"
        f"{extension}"
    )


def _document_path(
    root,
    label,
    filename,
):
    folder = _safe_slug(
        label,
        "item",
    )

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    return (
        f"{root}/"
        f"{folder}/"
        f"{uuid4().hex}"
        f"{extension}"
    )


def _safe_slug(
    value,
    fallback,
):
    slug = slugify(
        value or ""
    )

    return slug or fallback