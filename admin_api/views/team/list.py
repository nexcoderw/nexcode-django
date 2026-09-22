from admin_api.filters.team import (
    TeamFilterError,
    apply_team_filters,
)
from admin_api.pagination.page_number import (
    PaginationError,
    paginate_queryset,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.team import (
    serialize_team_member,
)
from admin_api.views.team.responses import (
    json_response,
    method_not_allowed,
)
from home.models import Team


@nexcode_admin_required
def list_team_view(request):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_team_filters(
                Team.objects.all(),
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
        TeamFilterError,
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
                    serialize_team_member(
                        member
                    )
                    for member
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )