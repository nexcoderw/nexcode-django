from admin_api.forms.client import (
    ClientCreateForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.client import (
    serialize_client,
)
from admin_api.services.client import (
    create_client,
)
from admin_api.views.client.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
)


@nexcode_admin_required
def add_client_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = ClientCreateForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    client = create_client(
        form.cleaned_data
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Client created.",
            "data": {
                "client":
                    serialize_client(
                        client
                    ),
            },
        },
        status=201,
    )
