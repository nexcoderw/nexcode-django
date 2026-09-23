from django.http import JsonResponse

from admin_api.serializers.portfolio import (
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
    methods,
):
    response = json_response(
        {
            "status": "error",
            "message":
                "Method not allowed.",
        },
        status=405,
    )

    response["Allow"] = (
        ", ".join(methods)
    )

    return response


def form_error(form):
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


def portfolio_not_found():
    return _not_found(
        "Portfolio not found."
    )


def image_not_found():
    return _not_found(
        "Portfolio image not found."
    )


def document_not_found():
    return _not_found(
        "Portfolio document not found."
    )


def repository_not_found():
    return _not_found(
        (
            "Portfolio repository "
            "not found."
        )
    )


def payload_error(error):
    return json_response(
        {
            "status": "error",
            "message": str(error),
        },
        status=error.status,
    )


def _not_found(message):
    return json_response(
        {
            "status": "error",
            "message": message,
        },
        status=404,
    )