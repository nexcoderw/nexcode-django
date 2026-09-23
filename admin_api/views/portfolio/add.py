from admin_api.forms.portfolio import (
    PortfolioCreateForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_detail,
)
from admin_api.services.portfolio import (
    create_portfolio,
)
from admin_api.views.portfolio.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
)


@nexcode_admin_required
def add_portfolio_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    try:
        payload = (
            parse_json_payload(
                request
            )
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = PortfolioCreateForm(
        payload
    )

    if not form.is_valid():
        return form_error(form)

    portfolio = create_portfolio(
        form
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Portfolio created.",
            "data": {
                "portfolio":
                    serialize_portfolio_detail(
                        portfolio
                    ),
            },
        },
        status=201,
    )