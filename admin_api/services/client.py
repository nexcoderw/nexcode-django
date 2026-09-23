import logging

from django.db import transaction

from home.models import Client


logger = logging.getLogger(
    __name__
)

FILE_FIELDS = (
    "profile_image",
)

TEXT_FIELDS = (
    "name",
    "company_name",
    "email",
    "phone",
    "website",
    "location",
    "notes",
    "status",
)


def create_client(
    cleaned_data,
):
    client = Client(
        name=cleaned_data[
            "name"
        ],
        company_name=(
            cleaned_data.get(
                "company_name"
            )
            or ""
        ),
        email=(
            cleaned_data.get(
                "email"
            )
            or ""
        ),
        phone=(
            cleaned_data.get(
                "phone"
            )
            or ""
        ),
        website=(
            cleaned_data.get(
                "website"
            )
            or ""
        ),
        location=(
            cleaned_data.get(
                "location"
            )
            or ""
        ),
        profile_image=(
            cleaned_data.get(
                "profile_image"
            )
        ),
        notes=(
            cleaned_data.get(
                "notes"
            )
            or ""
        ),
        status=(
            cleaned_data.get(
                "status"
            )
            or Client.Status.ACTIVE
        ),
    )

    try:
        with transaction.atomic():
            client.save()
    except Exception:
        _delete_failed_uploads(
            client,
            {},
        )

        raise

    return client


def update_client(
    client,
    form,
):
    original_files = {
        field_name: _file_name(
            getattr(
                client,
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

        if field_name == "name":
            setattr(
                client,
                field_name,
                value,
            )

            continue

        setattr(
            client,
            field_name,
            value or "",
        )

    if (
        "profile_image"
        in form.files
    ):
        client.profile_image = (
            data["profile_image"]
        )

    if data.get(
        "remove_profile_image"
    ):
        client.profile_image = None

    try:
        with transaction.atomic():
            client.save()
    except Exception:
        _delete_failed_uploads(
            client,
            original_files,
        )

        raise

    return client


def delete_client(
    client,
):
    with transaction.atomic():
        client.delete()


def _delete_failed_uploads(
    client,
    original_files,
):
    for field_name in FILE_FIELDS:
        file_value = getattr(
            client,
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
                "an uncommitted client "
                "upload.",
                extra={
                    "storage_name":
                        current_name,
                },
            )


def _file_name(
    file_value,
):
    return getattr(
        file_value,
        "name",
        "",
    )