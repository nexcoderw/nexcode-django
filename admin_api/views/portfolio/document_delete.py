from django.http import HttpResponse

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.portfolio import (
    delete_portfolio_document,
)
from admin_api.views.portfolio.responses import (
    document_not_found,
    method_not_allowed,
)
from home.models import PortfolioDocument


@nexcode_admin_required
def delete_portfolio_document_view(
    request,
    document_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    document = (
        PortfolioDocument.objects
        .filter(
            pk=document_id
        )
        .first()
    )

    if document is None:
        return document_not_found()

    delete_portfolio_document(
        document
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response