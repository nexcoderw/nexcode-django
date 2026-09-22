from admin_api.forms.team import (
    TeamCreateForm,
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
    create_team_member,
)
from admin_api.views.team.responses import (
    form_error,
    json_response,
    method_not_allowed,
)


@nexcode_admin_required
def add_team_view(request):
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

    form = TeamCreateForm(
        data,
        files,
    )

    if not form.is_valid():
        return form_error(form)

    team_member = (
        create_team_member(
            form.cleaned_data
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Team member created.",
            "data": {
                "team_member":
                    serialize_team_member(
                        team_member
                    ),
            },
        },
        status=201,
    )