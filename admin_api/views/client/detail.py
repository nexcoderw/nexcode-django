from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.client import (
    serialize_client_detail,
)
from admin_api.views.client.responses import (
    client_not_found,
    json_response,
    method_not_allowed,
)
from home.models import Client


@nexcode_admin_required
def client_detail_view(
    request,
    client_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    client = (
        Client.objects.filter(
            pk=client_id
        ).first()
    )

    if client is None:
        return client_not_found()

    return json_response(
        {
            "status": "success",
            "data": {
                "client":
                    serialize_client_detail(
                        client
                    ),
            },
        }
    )