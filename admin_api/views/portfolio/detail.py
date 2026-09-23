from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_detail,
)
from admin_api.views.portfolio.responses import (
    json_response,
    method_not_allowed,
    portfolio_not_found,
)
from home.models import Portfolio


@nexcode_admin_required
def portfolio_detail_view(
    request,
    portfolio_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    portfolio = (
        Portfolio.objects
        .prefetch_related(
            "team_members",
            "images",
            "documents",
            "repositories",
        )
        .filter(
            pk=portfolio_id
        )
        .first()
    )

    if portfolio is None:
        return portfolio_not_found()

    return json_response(
        {
            "status": "success",
            "data": {
                "portfolio":
                    serialize_portfolio_detail(
                        portfolio
                    ),
            },
        }
    )