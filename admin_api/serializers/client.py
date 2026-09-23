def serialize_client_summary(
    client,
):
    return {
        "id": client.pk,
        "name": client.name,
        "slug": client.slug,
        "company_name":
            client.company_name,
        "email":
            client.email
            or None,
        "phone":
            client.phone
            or None,
        "location":
            client.location
            or None,
        "profile_image":
            _file_url(
                client.profile_image
            ),
        "status":
            client.status,
        "created_at":
            _datetime_value(
                client.created_at
            ),
        "updated_at":
            _datetime_value(
                client.updated_at
            ),
    }


def serialize_client_detail(
    client,
):
    return {
        "id": client.pk,
        "name": client.name,
        "slug": client.slug,
        "company_name":
            client.company_name,
        "email":
            client.email
            or None,
        "phone":
            client.phone
            or None,
        "website":
            client.website
            or None,
        "location":
            client.location
            or None,
        "profile_image":
            _file_url(
                client.profile_image
            ),
        "notes":
            client.notes,
        "status":
            client.status,
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


def _file_url(
    file_field,
):
    if not file_field:
        return None

    try:
        return file_field.url
    except ValueError:
        return None


def _datetime_value(
    value,
):
    return (
        value.isoformat()
        if value
        else None
    )