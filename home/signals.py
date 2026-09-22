from django.db import (
    models,
    transaction,
)
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_save,
)

from home.models import (
    Blog,
    Client,
    Portfolio,
    PortfolioImage,
    Setting,
    Team,
    Training,
)


FILE_MODELS = (
    Blog,
    Client,
    Portfolio,
    PortfolioImage,
    Setting,
    Team,
    Training,
)


def capture_replaced_files(
    sender,
    instance,
    **kwargs,
):
    if not instance.pk:
        return

    try:
        previous = (
            sender.objects.get(
                pk=instance.pk
            )
        )
    except sender.DoesNotExist:
        return

    replaced = []

    for field in _file_fields(
        sender
    ):
        old_file = getattr(
            previous,
            field.name,
        )

        new_file = getattr(
            instance,
            field.name,
        )

        old_name = getattr(
            old_file,
            "name",
            "",
        )

        new_name = getattr(
            new_file,
            "name",
            "",
        )

        if (
            old_name
            and old_name
            != new_name
        ):
            replaced.append(
                (
                    old_file.storage,
                    old_name,
                )
            )

    instance._replaced_media_files = (
        replaced
    )


def delete_replaced_files(
    sender,
    instance,
    **kwargs,
):
    replaced = getattr(
        instance,
        "_replaced_media_files",
        (),
    )

    for storage, name in replaced:
        _delete_after_commit(
            storage,
            name,
        )

    if hasattr(
        instance,
        "_replaced_media_files",
    ):
        delattr(
            instance,
            "_replaced_media_files",
        )


def delete_instance_files(
    sender,
    instance,
    **kwargs,
):
    for field in _file_fields(
        sender
    ):
        file_value = getattr(
            instance,
            field.name,
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


def _file_fields(model):
    return (
        field
        for field in model._meta.fields
        if isinstance(
            field,
            models.FileField,
        )
    )


def _delete_after_commit(
    storage,
    name,
):
    transaction.on_commit(
        lambda: storage.delete(
            name
        )
    )


for model in FILE_MODELS:
    pre_save.connect(
        capture_replaced_files,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"capture-replaced-files-"
            f"{model._meta.label_lower}"
        ),
    )

    post_save.connect(
        delete_replaced_files,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"delete-replaced-files-"
            f"{model._meta.label_lower}"
        ),
    )

    post_delete.connect(
        delete_instance_files,
        sender=model,
        weak=False,
        dispatch_uid=(
            f"delete-instance-files-"
            f"{model._meta.label_lower}"
        ),
    )