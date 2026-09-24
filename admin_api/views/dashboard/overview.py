from django.utils import timezone

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.services.dashboard import (
    DashboardCurrencyError,
    build_overview,
)
from admin_api.views.contact.responses import (
    json_response,
    method_not_allowed,
)


@nexcode_admin_required
def dashboard_overview_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    currency = (
        request.GET.get(
            "currency",
            "",
        ).strip()
        or None
    )

    try:
        overview = build_overview(
            timezone.localdate(),
            currency,
        )
    except DashboardCurrencyError as error:
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
            "data": overview,
        }
    )
