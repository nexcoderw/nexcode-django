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


def serialize_admin_contact(
    contact,
):
    """A contact message with the sender details only admins may see."""
    return {
        **serialize_contact(
            contact
        ),
        "ip_address":
            contact.ip_address,
        "user_agent":
            contact.user_agent
            or None,
        "device_type":
            contact.device_type,
        "browser":
            contact.browser
            or None,
        "operating_system":
            contact.operating_system
            or None,
        "replied_at":
            _datetime_value(
                contact.replied_at
            ),
    }


def serialize_contact_reply(
    reply,
):
    sender = reply.sent_by

    return {
        "id": reply.pk,
        "subject": reply.subject,
        "message": reply.message,
        "sent_by":
            (
                sender.get_full_name()
                or sender.email
            )
            if sender
            else None,
        "sent_at":
            _datetime_value(
                reply.sent_at
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