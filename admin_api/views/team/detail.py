from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.team import (
    serialize_team_member,
)
from admin_api.views.team.responses import (
    json_response,
    method_not_allowed,
    team_not_found,
)
from home.models import Team


@nexcode_admin_required
def team_detail_view(
    request,
    team_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    team_member = (
        Team.objects.filter(
            pk=team_id
        ).first()
    )

    if team_member is None:
        return team_not_found()

    return json_response(
        {
            "status": "success",
            "data": {
                "team_member":
                    serialize_team_member(
                        team_member
                    ),
            },
        }
    )