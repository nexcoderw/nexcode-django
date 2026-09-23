import json


class JsonPayloadError(
    ValueError
):
    def __init__(
        self,
        message,
        status=400,
    ):
        super().__init__(
            message
        )

        self.status = status


def parse_json_payload(
    request,
):
    content_type = (
        request.content_type
        or ""
    )

    if (
        content_type
        != "application/json"
    ):
        raise JsonPayloadError(
            (
                "Expected an "
                "application/json "
                "request."
            ),
            status=415,
        )

    try:
        payload = json.loads(
            request.body
            or b"{}"
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        raise JsonPayloadError(
            "Invalid JSON payload."
        ) from error

    if not isinstance(
        payload,
        dict,
    ):
        raise JsonPayloadError(
            (
                "The request body "
                "must be a JSON object."
            )
        )

    return payload