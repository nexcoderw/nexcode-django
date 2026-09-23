from admin_api.forms.portfolio import (
    PortfolioUpdateForm,
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
    update_portfolio,
)
from admin_api.views.portfolio.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
    portfolio_not_found,
)
from home.models import Portfolio


@nexcode_admin_required
def update_portfolio_view(
    request,
    portfolio_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    portfolio = (
        Portfolio.objects.filter(
            pk=portfolio_id
        ).first()
    )

    if portfolio is None:
        return portfolio_not_found()

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

    form = PortfolioUpdateForm(
        payload,
        portfolio=portfolio,
    )

    if not form.is_valid():
        return form_error(form)

    portfolio = update_portfolio(
        portfolio,
        form,
    )

    portfolio = (
        Portfolio.objects
        .prefetch_related(
            "team_members",
            "images",
            "documents",
            "repositories",
        )
        .get(
            pk=portfolio.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Portfolio updated.",
            "data": {
                "portfolio":
                    serialize_portfolio_detail(
                        portfolio
                    ),
            },
        }
    )