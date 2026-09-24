from admin_api.filters.contact import (
    ContactFilterError,
    apply_contact_filters,
)
from admin_api.pagination.page_number import (
    PaginationError,
    paginate_queryset,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.contact import (
    serialize_admin_contact,
)
from admin_api.views.contact.responses import (
    json_response,
    method_not_allowed,
)
from home.models import Contact


@nexcode_admin_required
def list_contact_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_contact_filters(
                Contact.objects.all(),
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
        ContactFilterError,
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
                    serialize_admin_contact(
                        contact
                    )
                    for contact
                    in page.object_list
                ],
                "pagination":
                    pagination,
                # Shown as a count on the admin page, whatever the filters.
                "unanswered":
                    Contact.objects.filter(
                        replied_at__isnull=True,
                    ).count(),
            },
        }
    )
