from admin_api.forms.portfolio import (
    PortfolioImageCreateForm,
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
    create_portfolio_image,
)
from admin_api.views.portfolio.responses import (
    form_error,
    json_response,
    method_not_allowed,
    portfolio_not_found,
)
from home.models import Portfolio


@nexcode_admin_required
def add_portfolio_image_view(
    request,
    portfolio_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    portfolio = (
        Portfolio.objects.filter(
            pk=portfolio_id
        ).first()
    )

    if portfolio is None:
        return portfolio_not_found()

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

    form = PortfolioImageCreateForm(
        data,
        files,
    )

    if not form.is_valid():
        return form_error(form)

    image = create_portfolio_image(
        portfolio,
        form,
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Portfolio image added.",
            "data": {
                "image":
                    serialize_portfolio_image(
                        image
                    ),
            },
        },
        status=201,
    )