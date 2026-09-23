from django.http import HttpResponse

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.portfolio import (
    delete_portfolio_image,
)
from admin_api.views.portfolio.responses import (
    image_not_found,
    method_not_allowed,
)
from home.models import PortfolioImage


@nexcode_admin_required
def delete_portfolio_image_view(
    request,
    image_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    image = (
        PortfolioImage.objects
        .filter(
            pk=image_id
        )
        .first()
    )

    if image is None:
        return image_not_found()

    delete_portfolio_image(
        image
    )

    response = HttpResponse(
        status=204
    )

    response[
        "Cache-Control"
    ] = "no-store"

    return response