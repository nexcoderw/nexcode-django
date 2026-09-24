from django.http import (
    JsonResponse,
)

from admin_api.serializers.contact import (
    serialize_form_errors,
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


def payload_error(
    error,
):
    return json_response(
        {
            "status": "error",
            "message": str(
                error
            ),
        },
        status=error.status,
    )


def form_error(
    form,
):

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


def too_many_requests():
    return json_response(
        {
            "status": "error",
            "message": (
                "Too many messages "
                "sent. Please try "
                "again later."
            ),
        },
        status=429,
    )


def contact_not_found():
    return json_response(
        {
            "status": "error",
            "message":
                "Contact not found.",
        },
        status=404,
    )


def email_not_sent():
    return json_response(
        {
            "status": "error",
            "message": (
                "The email could "
                "not be sent."
            ),
        },
        status=502,
    )
