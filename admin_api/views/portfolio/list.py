from django.db.models import (
    Count,
    Prefetch,
)

from admin_api.filters.portfolio import (
    PortfolioFilterError,
    apply_portfolio_filters,
)
from admin_api.pagination.page_number import (
    PaginationError,
    paginate_queryset,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_summary,
)
from admin_api.views.portfolio.responses import (
    json_response,
    method_not_allowed,
)
from home.models import (
    Portfolio,
    PortfolioImage,
)


@nexcode_admin_required
def list_portfolio_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    queryset = (
        Portfolio.objects
        .annotate(
            team_member_count=Count(
                "team_members",
                distinct=True,
            )
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=(
                    PortfolioImage
                    .objects
                    .filter(
                        is_cover=True
                    )
                    .order_by("pk")
                ),
                to_attr=(
                    "cover_images"
                ),
            )
        )
    )

    try:
        queryset = (
            apply_portfolio_filters(
                queryset,
                request.GET,
            )
        )

        page, pagination = (
            paginate_queryset(
                queryset,
                request.GET,
            )
        )
    except (
        PortfolioFilterError,
        PaginationError,
    ) as error:
        return json_response(
            {
                "status": "error",
                "message": str(
                    error
                ),
            },
            status=400,
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_portfolio_summary(
                        portfolio
                    )
                    for portfolio
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )