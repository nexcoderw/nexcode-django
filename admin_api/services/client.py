from django.db import transaction

from admin_api.forms.client import CLIENT_FIELDS
from home.models import Client


def create_client(
    cleaned_data,
):
    client = Client(
        name=cleaned_data["name"],
        email=(
            cleaned_data.get("email")
            or ""
        ),
        phone_number=(
            cleaned_data.get(
                "phone_number"
            )
            or ""
        ),
    )

    with transaction.atomic():
        client.save()

    return client


def update_client(
    client,
    form,
):
    data = form.cleaned_data

    # Only fields present in the request change; an omitted field keeps
    # its stored value, and an empty optional one clears it.
    for field_name in CLIENT_FIELDS:
        if field_name not in form.data:
            continue

        setattr(
            client,
            field_name,
            data.get(field_name) or "",
        )

    with transaction.atomic():
        client.save()

    return client


def delete_client(
    client,
):
    with transaction.atomic():
        client.delete()
