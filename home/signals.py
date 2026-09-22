import logging

from django.db import transaction
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_save,
)
from django.dispatch import receiver

from home.models import Team


logger = logging.getLogger(
    __name__
)

TEAM_FILE_FIELDS = (
    "image",
    "image_png",
)


@receiver(
    pre_save,
    sender=Team,
)
def capture_replaced_team_files(
    sender,
    instance,
    **kwargs,
):
    if not instance.pk:
        return

    previous = (
        Team.objects.filter(
            pk=instance.pk
        ).first()
    )

    if previous is None:
        return

    replaced_files = []

    for field_name in (
        TEAM_FILE_FIELDS
    ):
        previous_file = getattr(
            previous,
            field_name,
        )

        current_file = getattr(
            instance,
            field_name,
        )

        previous_name = getattr(
            previous_file,
            "name",
            "",
        )

        current_name = getattr(
            current_file,
            "name",
            "",
        )

        if (
            previous_name
            and previous_name
            != current_name
        ):
            replaced_files.append(
                (
                    previous_file.storage,
                    previous_name,
                )
            )

    instance._replaced_team_files = (
        replaced_files
    )


@receiver(
    post_save,
    sender=Team,
)
def delete_replaced_team_files(
    sender,
    instance,
    **kwargs,
):
    replaced_files = getattr(
        instance,
        "_replaced_team_files",
        (),
    )

    for storage, name in (
        replaced_files
    ):
        _delete_after_commit(
            storage,
            name,
        )

    if hasattr(
        instance,
        "_replaced_team_files",
    ):
        delattr(
            instance,
            "_replaced_team_files",
        )


@receiver(
    post_delete,
    sender=Team,
)
def delete_team_files(
    sender,
    instance,
    **kwargs,
):
    for field_name in (
        TEAM_FILE_FIELDS
    ):
        file_value = getattr(
            instance,
            field_name,
        )

        name = getattr(
            file_value,
            "name",
            "",
        )

        if not name:
            continue

        _delete_after_commit(
            file_value.storage,
            name,
        )


def _delete_after_commit(
    storage,
    name,
):
    transaction.on_commit(
        lambda: _safe_delete(
            storage,
            name,
        )
    )


def _safe_delete(
    storage,
    name,
):
    try:
        storage.delete(name)
    except Exception:
        logger.exception(
            "Failed to delete media file.",
            extra={
                "storage_name": name,
            },
        )