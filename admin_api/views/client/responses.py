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


def client_not_found():
    return json_response(
        {
            "status": "error",
            "message":
                "Client not found.",
        },
        status=404,
    )


def payload_error(
    error,
):
    return json_response(
        {
            "status": "error",
            "message": str(error),
        },
        status=error.status,
    )


def form_error(
    form,
):
    from admin_api.serializers.client import (
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