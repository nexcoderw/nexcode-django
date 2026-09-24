from admin_api.forms.contact import (
    ContactReplyForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.contact import (
    serialize_admin_contact,
    serialize_contact_reply,
)
from admin_api.services.contact_reply import (
    ContactReplyNotSent,
    send_contact_reply,
)
from admin_api.views.contact.responses import (
    contact_not_found,
    email_not_sent,
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
)
from home.models import Contact


@nexcode_admin_required
def reply_contact_view(
    request,
    contact_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    contact = (
        Contact.objects.filter(
            pk=contact_id
        ).first()
    )

    if contact is None:
        return contact_not_found()

    try:
        payload = (
            parse_json_payload(
                request
            )
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = ContactReplyForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        reply = send_contact_reply(
            contact,
            form.cleaned_data,
            request.user,
        )
    except ContactReplyNotSent:
        return email_not_sent()

    return json_response(
        {
            "status": "success",
            "message": (
                "Your reply "
                "has been sent."
            ),
            "data": {
                "contact":
                    serialize_admin_contact(
                        contact
                    ),
                "reply":
                    serialize_contact_reply(
                        reply
                    ),
            },
        },
        status=201,
    )
