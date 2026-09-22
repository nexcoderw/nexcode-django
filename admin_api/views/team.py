from django.http import (
    HttpResponse,
    JsonResponse,
)

from admin_api.filters.team import (
    apply_team_filters,
)
from admin_api.forms.team import (
    TeamCreateForm,
    TeamUpdateForm,
)
from admin_api.pagination.page_number import (
    paginate_queryset,
)
from admin_api.parsers.multipart import (
    MultipartPayloadError,
    parse_multipart_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.team import (
    serialize_form_errors,
    serialize_team_member,
)
from admin_api.services.team import (
    create_team_member,
    delete_team_member,
    update_team_member,
)
from home.models import Team


@nexcode_admin_required
def team_collection_view(
    request,
):
    if request.method == "GET":
        return _list_team(
            request
        )

    if request.method == "POST":
        return _create_team(
            request
        )

    return _method_not_allowed(
        ["GET", "POST"]
    )


@nexcode_admin_required
def team_item_view(
    request,
    team_id,
):
    team_member = (
        Team.objects.filter(
            pk=team_id
        ).first()
    )

    if team_member is None:
        return _json_response(
            {
                "status": "error",
                "message":
                    "Team member not found.",
            },
            status=404,
        )

    if request.method == "GET":
        return _json_response(
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

    if request.method == "PATCH":
        return _update_team(
            request,
            team_member,
        )

    if request.method == "DELETE":
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

    return _method_not_allowed(
        [
            "GET",
            "PATCH",
            "DELETE",
        ]
    )


def _list_team(request):
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
    except ValueError as error:
        return _json_response(
            {
                "status": "error",
                "message": str(
                    error
                ),
            },
            status=400,
        )

    return _json_response(
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


def _create_team(request):
    payload = (
        _mutation_payload(
            request
        )
    )

    if isinstance(
        payload,
        JsonResponse,
    ):
        return payload

    data, files = payload

    form = TeamCreateForm(
        data,
        files,
    )

    if not form.is_valid():
        return _form_error(
            form
        )

    team_member = (
        create_team_member(
            form.cleaned_data
        )
    )

    return _json_response(
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


def _update_team(
    request,
    team_member,
):
    payload = (
        _mutation_payload(
            request
        )
    )

    if isinstance(
        payload,
        JsonResponse,
    ):
        return payload

    data, files = payload

    form = TeamUpdateForm(
        data,
        files,
    )

    if not form.is_valid():
        return _form_error(
            form
        )

    team_member = (
        update_team_member(
            team_member,
            form,
        )
    )

    return _json_response(
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


def _mutation_payload(
    request,
):
    try:
        return (
            parse_multipart_payload(
                request
            )
        )
    except MultipartPayloadError as error:
        return _json_response(
            {
                "status": "error",
                "message": str(
                    error
                ),
            },
            status=415,
        )


def _form_error(form):
    return _json_response(
        {
            "status": "error",
            "message":
                "Check the submitted fields.",
            "errors":
                serialize_form_errors(
                    form
                ),
        },
        status=400,
    )


def _json_response(
    payload,
    status=200,
):
    response = JsonResponse(
        payload,
        status=status,
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response


def _method_not_allowed(
    allowed_methods,
):
    response = _json_response(
        {
            "status": "error",
            "message":
                "Method not allowed.",
        },
        status=405,
    )

    response["Allow"] = ", ".join(
        allowed_methods
    )

    return response