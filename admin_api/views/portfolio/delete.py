from django.http import HttpResponse

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.portfolio import (
    delete_portfolio,
)
from admin_api.views.portfolio.responses import (
    method_not_allowed,
    portfolio_not_found,
)
from home.models import Portfolio


@nexcode_admin_required
def delete_portfolio_view(
    request,
    portfolio_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    portfolio = (
        Portfolio.objects.filter(
            pk=portfolio_id
        ).first()
    )

    if portfolio is None:
        return portfolio_not_found()

    delete_portfolio(
        portfolio
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response