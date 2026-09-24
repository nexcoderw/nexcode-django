from admin_api.filters.client import (
    ClientFilterError,
    apply_client_filters,
)
from admin_api.pagination.page_number import (
    PaginationError,
    paginate_queryset,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.client import (
    serialize_client,
)
from admin_api.views.client.responses import (
    json_response,
    method_not_allowed,
)
from home.models import Client


@nexcode_admin_required
def list_client_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_client_filters(
                Client.objects.all(),
                request.GET,
            )
        )

        page, pagination = (
            paginate_queryset(
                queryset,
                request.GET,
            )
        )

    except (
        ClientFilterError,
        PaginationError,
    ) as error:
        return json_response(
            {
                "status": "error",
                "message": str(
                    error
                ),
            },
            status=400,
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_client(
                        client
                    )
                    for client
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )