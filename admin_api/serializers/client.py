def serialize_client(
    client,
):
    return {
        "id": client.pk,
        "name": client.name,
        "email":
            client.email
            or None,
        "phone_number":
            client.phone_number
            or None,
        "created_at":
            _datetime_value(
                client.created_at
            ),
        "updated_at":
            _datetime_value(
                client.updated_at
            ),
    }


def serialize_form_errors(
    form,
):
    return {
        field: [
            str(error)
            for error in errors
        ]
        for field, errors
        in form.errors.items()
    }


def _datetime_value(
    value,
):
    return (
        value.isoformat()
        if value
        else None
    )
