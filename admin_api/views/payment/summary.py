from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.payment.summary import (
    serialize_agreement_summary,
    serialize_portfolio_summary,
)
from admin_api.services.payment.summary import (
    get_portfolio_financial_summary,
)
from admin_api.views.payment.responses import (
    json_response,
    method_not_allowed,
    not_found,
)
from home.models import (
    PaymentAgreement,
    Portfolio,
)
from home.services.payment.status import (
    get_agreement_summary,
)


@nexcode_admin_required
def agreement_summary_view(
    request,
    agreement_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    agreement = (
        PaymentAgreement
        .objects
        .filter(
            pk=agreement_id
        )
        .first()
    )

    if agreement is None:
        return not_found(
            "Payment agreement"
        )

    summary = (
        get_agreement_summary(
            agreement
        )
    )

    return json_response(
        {
            "status": "success",
            "data": {
                "summary":
                    serialize_agreement_summary(
                        summary
                    ),
            },
        }
    )


@nexcode_admin_required
def portfolio_summary_view(
    request,
    portfolio_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    portfolio = (
        Portfolio.objects.filter(
            pk=portfolio_id
        ).first()
    )

    if portfolio is None:
        return not_found(
            "Portfolio"
        )

    summary = (
        get_portfolio_financial_summary(
            portfolio
        )
    )

    return json_response(
        {
            "status": "success",
            "data": {
                "summary":
                    serialize_portfolio_summary(
                        summary
                    ),
            },
        }
    )