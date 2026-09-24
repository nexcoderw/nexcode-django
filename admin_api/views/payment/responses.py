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
    allowed,
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
        allowed
    )

    return response


def not_found(
    resource,
):
    return json_response(
        {
            "status": "error",
            "message":
                f"{resource} not found.",
        },
        status=404,
    )


def payload_error(
    error,
):
    return json_response(
        {
            "status": "error",
            "message":
                str(error),
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
            "errors": {
                field: [
                    str(error)
                    for error
                    in errors
                ]
                for field, errors
                in form.errors.items()
            },
        },
        status=400,
    )


def operation_error(
    error,
):
    errors = {}

    if getattr(
        error,
        "field",
        None,
    ):
        errors[
            error.field
        ] = [
            str(error)
        ]

    return json_response(
        {
            "status": "error",
            "message":
                str(error),
            "errors":
                errors,
        },
        status=400,
    )