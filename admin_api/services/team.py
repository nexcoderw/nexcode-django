import logging

from django.db import transaction

from home.models import Team


logger = logging.getLogger(
    __name__
)

FILE_FIELDS = (
    "image",
    "image_png",
)

TEXT_FIELDS = (
    "name",
    "position",
    "linkedin",
    "github",
)


def create_team_member(
    cleaned_data,
):
    team_member = Team(
        name=cleaned_data["name"],
        position=(
            cleaned_data["position"]
        ),
        image=cleaned_data.get(
            "image"
        ),
        image_png=cleaned_data.get(
            "image_png"
        ),
        linkedin=(
            cleaned_data.get(
                "linkedin"
            )
            or None
        ),
        github=(
            cleaned_data.get(
                "github"
            )
            or None
        ),
    )

    try:
        with transaction.atomic():
            team_member.save()
    except Exception:
        _delete_failed_uploads(
            team_member,
            {},
        )

        raise

    return team_member


def update_team_member(
    team_member,
    form,
):
    original_files = {
        field_name: _file_name(
            getattr(
                team_member,
                field_name,
            )
        )
        for field_name
        in FILE_FIELDS
    }

    data = form.cleaned_data

    for field_name in TEXT_FIELDS:
        if field_name not in form.data:
            continue

        value = data.get(
            field_name
        )

        setattr(
            team_member,
            field_name,
            value or None,
        )

    if "image" in form.files:
        team_member.image = (
            data["image"]
        )

    if "image_png" in form.files:
        team_member.image_png = (
            data["image_png"]
        )

    if data.get(
        "remove_image"
    ):
        team_member.image = None

    if data.get(
        "remove_image_png"
    ):
        team_member.image_png = None

    try:
        with transaction.atomic():
            team_member.save()
    except Exception:
        _delete_failed_uploads(
            team_member,
            original_files,
        )

        raise

    return team_member


def delete_team_member(
    team_member,
):
    with transaction.atomic():
        team_member.delete()


def _delete_failed_uploads(
    team_member,
    original_files,
):
    for field_name in FILE_FIELDS:
        file_value = getattr(
            team_member,
            field_name,
        )

        current_name = _file_name(
            file_value
        )

        original_name = (
            original_files.get(
                field_name,
                "",
            )
        )

        if (
            not current_name
            or current_name
            == original_name
        ):
            continue

        try:
            file_value.storage.delete(
                current_name
            )
        except Exception:
            logger.exception(
                "Failed to clean up "
                "an uncommitted team upload.",
                extra={
                    "storage_name":
                        current_name,
                },
            )


def _file_name(file_value):
    return getattr(
        file_value,
        "name",
        "",
    )