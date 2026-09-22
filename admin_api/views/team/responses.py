from django.http import (
    JsonResponse,
)


def json_response(
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


def method_not_allowed(
    allowed_methods,
):
    response = json_response(
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


def team_not_found():
    return json_response(
        {
            "status": "error",
            "message":
                "Team member not found.",
        },
        status=404,
    )


def form_error(form):
    from admin_api.serializers.team import (
        serialize_form_errors,
    )

    return json_response(
        {
            "status": "error",
            "message": (
                "Check the submitted "
                "fields."
            ),
            "errors":
                serialize_form_errors(
                    form
                ),
        },
        status=400,
    )