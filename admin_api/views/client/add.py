from admin_api.forms.client import (
    ClientCreateForm,
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
    create_client,
)
from admin_api.views.client.responses import (
    form_error,
    json_response,
    method_not_allowed,
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

    form = ClientCreateForm(
        data,
        files,
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
                    serialize_client_detail(
                        client
                    ),
            },
        },
        status=201,
    )