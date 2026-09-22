from admin_api.forms.team import (
    TeamUpdateForm,
)
from admin_api.parsers.multipart import (
    MultipartPayloadError,
    parse_multipart_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.team import (
    serialize_team_member,
)
from admin_api.services.team import (
    update_team_member,
)
from admin_api.views.team.responses import (
    form_error,
    json_response,
    method_not_allowed,
    team_not_found,
)
from home.models import Team


@nexcode_admin_required
def update_team_view(
    request,
    team_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    team_member = (
        Team.objects.filter(
            pk=team_id
        ).first()
    )

    if team_member is None:
        return team_not_found()

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

    form = TeamUpdateForm(
        data,
        files,
    )

    if not form.is_valid():
        return form_error(form)

    team_member = (
        update_team_member(
            team_member,
            form,
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Team member updated.",
            "data": {
                "team_member":
                    serialize_team_member(
                        team_member
                    ),
            },
        }
    )