from django.http.multipartparser import (
    MultiPartParser,
    MultiPartParserError,
)


class MultipartPayloadError(
    ValueError
):
    pass


def parse_multipart_payload(
    request,
):
    content_type = (
        request.content_type
        or ""
    )

    if not content_type.startswith(
        "multipart/form-data"
    ):
        raise MultipartPayloadError(
            "Expected multipart form data."
        )

    if request.method == "POST":
        return (
            request.POST,
            request.FILES,
        )

    try:
        parser = MultiPartParser(
            request.META,
            request,
            request.upload_handlers,
            request.encoding,
        )

        return parser.parse()
    except MultiPartParserError as error:
        raise MultipartPayloadError(
            "Invalid multipart payload."
        ) from error