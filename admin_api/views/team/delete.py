from django.http import (
    HttpResponse,
)

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.team import (
    delete_team_member,
)
from admin_api.views.team.responses import (
    method_not_allowed,
    team_not_found,
)
from home.models import Team


@nexcode_admin_required
def delete_team_view(
    request,
    team_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    team_member = (
        Team.objects.filter(
            pk=team_id
        ).first()
    )

    if team_member is None:
        return team_not_found()

    delete_team_member(
        team_member
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response