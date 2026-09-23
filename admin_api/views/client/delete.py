from django.http import (
    HttpResponse,
)

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.client import (
    delete_client,
)
from admin_api.views.client.responses import (
    client_not_found,
    method_not_allowed,
)
from home.models import Client


@nexcode_admin_required
def delete_client_view(
    request,
    client_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    client = (
        Client.objects.filter(
            pk=client_id
        ).first()
    )

    if client is None:
        return client_not_found()

    delete_client(
        client
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response