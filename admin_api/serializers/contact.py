def serialize_contact(
    contact,
):
    return {
        "id": contact.pk,
        "name": contact.name,
        "email": contact.email,
        "subject": contact.subject,
        "message": contact.message,
        "created_at":
            _datetime_value(
                contact.created_at
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