import logging

from django.db import transaction
from django.db.models import Max

from home.models import (
    Portfolio,
    PortfolioDocument,
    PortfolioImage,
    PortfolioRepository,
)


logger = logging.getLogger(
    __name__
)


PORTFOLIO_FIELDS = (
    "name",
    "summary",
    "description",
    "category",
    "project_type",
    "live_url",
    "figma_url",
    "project_initiation_date",
    "deadline_date",
    "status",
)


def create_portfolio(
    form,
):
    data = form.cleaned_data

    portfolio = Portfolio(
        name=data["name"],
        summary=(
            data.get("summary")
            or ""
        ),
        description=(
            data.get("description")
            or ""
        ),
        category=data["category"],
        project_type=(
            data["project_type"]
        ),
        live_url=(
            data.get("live_url")
            or ""
        ),
        figma_url=(
            data.get("figma_url")
            or ""
        ),
        project_initiation_date=(
            data.get(
                "project_initiation_date"
            )
        ),
        deadline_date=(
            data.get(
                "deadline_date"
            )
        ),
        status=(
            data.get("status")
            or Portfolio.Status.DRAFT
        ),
    )

    with transaction.atomic():
        portfolio.full_clean()
        portfolio.save()

        portfolio.team_members.set(
            data.get(
                "team_member_ids"
            )
            or []
        )

    return portfolio


def update_portfolio(
    portfolio,
    form,
):
    data = form.cleaned_data

    with transaction.atomic():
        for field_name in (
            PORTFOLIO_FIELDS
        ):
            if (
                field_name
                not in form.data
            ):
                continue

            value = data.get(
                field_name
            )

            if field_name in {
                "summary",
                "description",
                "live_url",
                "figma_url",
            }:
                value = value or ""

            setattr(
                portfolio,
                field_name,
                value,
            )

        portfolio.full_clean()
        portfolio.save()

        if (
            "team_member_ids"
            in form.data
        ):
            portfolio.team_members.set(
                data.get(
                    "team_member_ids"
                )
                or []
            )

    return portfolio


def delete_portfolio(
    portfolio,
):
    with transaction.atomic():
        portfolio.delete()


def create_portfolio_image(
    portfolio,
    form,
):
    data = form.cleaned_data

    position = data.get(
        "position"
    )

    if position is None:
        maximum = (
            portfolio.images
            .aggregate(
                value=Max(
                    "position"
                )
            )["value"]
        )

        position = (
            0
            if maximum is None
            else maximum + 1
        )

    image = PortfolioImage(
        portfolio=portfolio,
        image=data["image"],
        alt_text=(
            data.get("alt_text")
            or ""
        ),
        is_cover=(
            data.get("is_cover")
            or False
        ),
        position=position,
    )

    try:
        with transaction.atomic():
            if image.is_cover:
                portfolio.images.update(
                    is_cover=False
                )

            image.full_clean()
            image.save()
    except Exception:
        _delete_uncommitted_image(
            image
        )

        raise

    return image


def update_portfolio_image(
    image,
    form,
):
    data = form.cleaned_data

    original_name = (
        image.image.name
        if image.image
        else ""
    )

    try:
        with transaction.atomic():
            if (
                "image"
                in form.files
            ):
                image.image = (
                    data["image"]
                )

            if (
                "alt_text"
                in form.data
            ):
                image.alt_text = (
                    data.get(
                        "alt_text"
                    )
                    or ""
                )

            if (
                "position"
                in form.data
            ):
                image.position = (
                    data["position"]
                )

            if (
                "is_cover"
                in form.data
            ):
                image.is_cover = (
                    data.get(
                        "is_cover"
                    )
                    or False
                )

                if image.is_cover:
                    (
                        image.portfolio
                        .images
                        .exclude(
                            pk=image.pk
                        )
                        .update(
                            is_cover=False
                        )
                    )

            image.full_clean()
            image.save()
    except Exception:
        _delete_uncommitted_image(
            image,
            original_name=(
                original_name
            ),
        )

        raise

    return image


def delete_portfolio_image(
    image,
):
    with transaction.atomic():
        image.delete()


def create_portfolio_document(
    portfolio,
    form,
):
    with transaction.atomic():
        document = (
            PortfolioDocument
            .objects.create(
                portfolio=portfolio,
                title=(
                    form.cleaned_data[
                        "title"
                    ]
                ),
                url=(
                    form.cleaned_data[
                        "url"
                    ]
                ),
            )
        )

    return document


def update_portfolio_document(
    document,
    form,
):
    with transaction.atomic():
        if (
            "title"
            in form.data
        ):
            document.title = (
                form.cleaned_data[
                    "title"
                ]
            )

        if (
            "url"
            in form.data
        ):
            document.url = (
                form.cleaned_data[
                    "url"
                ]
            )

        document.full_clean()
        document.save()

    return document


def delete_portfolio_document(
    document,
):
    with transaction.atomic():
        document.delete()


def create_portfolio_repository(
    portfolio,
    form,
):
    with transaction.atomic():
        repository = (
            PortfolioRepository
            .objects.create(
                portfolio=portfolio,
                label=(
                    form.cleaned_data.get(
                        "label"
                    )
                    or "Repository"
                ),
                url=(
                    form.cleaned_data[
                        "url"
                    ]
                ),
            )
        )

    return repository


def update_portfolio_repository(
    repository,
    form,
):
    with transaction.atomic():
        if (
            "label"
            in form.data
        ):
            repository.label = (
                form.cleaned_data.get(
                    "label"
                )
                or "Repository"
            )

        if (
            "url"
            in form.data
        ):
            repository.url = (
                form.cleaned_data[
                    "url"
                ]
            )

        repository.full_clean()
        repository.save()

    return repository


def delete_portfolio_repository(
    repository,
):
    with transaction.atomic():
        repository.delete()


def _delete_uncommitted_image(
    image,
    original_name="",
):
    file_value = image.image

    name = getattr(
        file_value,
        "name",
        "",
    )

    committed = getattr(
        file_value,
        "_committed",
        False,
    )

    if (
        not name
        or not committed
        or name == original_name
    ):
        return

    try:
        file_value.storage.delete(
            name
        )
    except Exception:
        logger.exception(
            (
                "Failed to clean up "
                "an uncommitted "
                "portfolio image."
            ),
            extra={
                "storage_name":
                    name,
            },
        )