from django.http import HttpResponse

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.portfolio import (
    delete_portfolio_repository,
)
from admin_api.views.portfolio.responses import (
    method_not_allowed,
    repository_not_found,
)
from home.models import PortfolioRepository


@nexcode_admin_required
def delete_portfolio_repository_view(
    request,
    repository_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    repository = (
        PortfolioRepository.objects
        .filter(
            pk=repository_id
        )
        .first()
    )

    if repository is None:
        return repository_not_found()

    delete_portfolio_repository(
        repository
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response