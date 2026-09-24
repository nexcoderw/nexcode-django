from admin_api.forms.contact import (
    ContactCreateForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.serializers.contact import (
    serialize_contact,
)
from admin_api.services.contact import (
    create_contact,
)
from admin_api.views.contact.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
    too_many_requests,
)
from home.contact_sender import (
    sender_details,
)
from home.contact_throttle import (
    allow_contact_submission,
)


def add_contact_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

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

    form = ContactCreateForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    sender = sender_details(
        request
    )

    if not allow_contact_submission(
        sender["ip_address"]
    ):
        return too_many_requests()

    contact = create_contact(
        form.cleaned_data,
        sender,
    )

    return json_response(
        {
            "status": "success",
            "message": (
                "Your message "
                "has been received."
            ),
            "data": {
                "contact":
                    serialize_contact(
                        contact
                    ),
            },
        },
        status=201,
    )