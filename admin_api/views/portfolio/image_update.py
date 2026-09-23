from admin_api.forms.portfolio import (
    PortfolioImageUpdateForm,
)
from admin_api.parsers.multipart import (
    MultipartPayloadError,
    parse_multipart_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_image,
)
from admin_api.services.portfolio import (
    update_portfolio_image,
)
from admin_api.views.portfolio.responses import (
    form_error,
    image_not_found,
    json_response,
    method_not_allowed,
)
from home.models import PortfolioImage


@nexcode_admin_required
def update_portfolio_image_view(
    request,
    image_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    image = (
        PortfolioImage.objects
        .select_related(
            "portfolio"
        )
        .filter(
            pk=image_id
        )
        .first()
    )

    if image is None:
        return image_not_found()

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
                "message": str(error),
            },
            status=415,
        )

    form = PortfolioImageUpdateForm(
        data,
        files,
    )

    if not form.is_valid():
        return form_error(form)

    image = update_portfolio_image(
        image,
        form,
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Portfolio image updated.",
            "data": {
                "image":
                    serialize_portfolio_image(
                        image
                    ),
            },
        }
    )