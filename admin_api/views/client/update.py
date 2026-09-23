from admin_api.forms.client import (
    ClientUpdateForm,
)
from admin_api.parsers.multipart import (
    MultipartPayloadError,
    parse_multipart_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.client import (
    serialize_client_detail,
)
from admin_api.services.client import (
    update_client,
)
from admin_api.views.client.responses import (
    client_not_found,
    form_error,
    json_response,
    method_not_allowed,
)
from home.models import Client


@nexcode_admin_required
def update_client_view(
    request,
    client_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    client = (
        Client.objects.filter(
            pk=client_id
        ).first()
    )

    if client is None:
        return client_not_found()

    try:
        data, files = (
            parse_multipart_payload(
                request
            )
        )
    except MultipartPayloadError as error:
        return json_response(
            {
                "status": "error",
                "message": str(
                    error
                ),
            },
            status=415,
        )

    form = ClientUpdateForm(
        data,
        files,
    )

    if not form.is_valid():
        return form_error(
            form
        )

    client = update_client(
        client,
        form,
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Client updated.",
            "data": {
                "client":
                    serialize_client_detail(
                        client
                    ),
            },
        }
    )