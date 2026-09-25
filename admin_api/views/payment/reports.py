from django.http import (
    HttpResponse,
)

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.payment.report import (
    serialize_payment_report,
)
from admin_api.services.payment.report import (
    PaymentReportError,
    build_payment_receipt_pdf,
    build_portfolio_statement_pdf,
    get_collections_report,
    get_outstanding_report,
    get_payment_receipt,
    get_portfolio_statement,
    get_report_overview,
    parse_payment_report_filters,
    payment_receipt_number,
)
from admin_api.views.payment.responses import (
    json_response,
    method_not_allowed,
    not_found,
)
from home.models import (
    PaymentRecord,
    Portfolio,
)


@nexcode_admin_required
def report_overview_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    filters, error = (
        _report_filters(
            request
        )
    )

    if error:
        return error

    return json_response(
        {
            "status":
                "success",

            "data": {
                "overview":
                    serialize_payment_report(
                        get_report_overview(
                            filters
                        )
                    ),
            },
        }
    )


@nexcode_admin_required
def collections_report_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    filters, error = (
        _report_filters(
            request
        )
    )

    if error:
        return error

    return json_response(
        {
            "status":
                "success",

            "data": {
                "report":
                    serialize_payment_report(
                        get_collections_report(
                            filters
                        )
                    ),
            },
        }
    )


@nexcode_admin_required
def outstanding_report_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    filters, error = (
        _report_filters(
            request
        )
    )

    if error:
        return error

    return json_response(
        {
            "status":
                "success",

            "data": {
                "report":
                    serialize_payment_report(
                        get_outstanding_report(
                            filters
                        )
                    ),
            },
        }
    )


@nexcode_admin_required
def portfolio_statement_view(
    request,
    portfolio_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    portfolio = (
        Portfolio.objects
        .filter(
            pk=portfolio_id
        )
        .first()
    )

    if portfolio is None:
        return not_found(
            "Portfolio"
        )

    statement = (
        get_portfolio_statement(
            portfolio
        )
    )

    if (
        request.GET.get(
            "format"
        )
        == "pdf"
    ):
        return _pdf_response(
            build_portfolio_statement_pdf(
                statement
            ),
            (
                "portfolio-"
                f"{portfolio.pk}-"
                "payment-statement.pdf"
            ),
        )

    return json_response(
        {
            "status":
                "success",

            "data": {
                "statement":
                    serialize_payment_report(
                        statement
                    ),
            },
        }
    )


@nexcode_admin_required
def payment_receipt_view(
    request,
    payment_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    payment = (
        PaymentRecord.objects
        .select_related(
            "agreement",
            "agreement__portfolio",
            "recorded_by",
        )
        .prefetch_related(
            "allocations__installment"
        )
        .filter(
            pk=payment_id
        )
        .first()
    )

    if payment is None:
        return not_found(
            "Payment record"
        )

    receipt = (
        get_payment_receipt(
            payment
        )
    )

    if (
        request.GET.get(
            "format"
        )
        == "pdf"
    ):
        return _pdf_response(
            build_payment_receipt_pdf(
                receipt
            ),
            (
                payment_receipt_number(
                    payment.pk
                )
                + ".pdf"
            ),
        )

    return json_response(
        {
            "status":
                "success",

            "data": {
                "receipt":
                    serialize_payment_report(
                        receipt
                    ),
            },
        }
    )


def _report_filters(
    request,
):
    try:
        return (
            parse_payment_report_filters(
                request.GET
            ),
            None,
        )

    except PaymentReportError:
        return (
            None,
            json_response(
                {
                    "status":
                        "error",

                    "message": (
                        "Check the "
                        "report filters."
                    ),
                },
                status=400,
            ),
        )


def _pdf_response(
    body,
    filename,
):
    response = HttpResponse(
        body,
        content_type=(
            "application/pdf"
        ),
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="{filename}"'
    )

    response[
        "Cache-Control"
    ] = "no-store"

    response[
        "X-Content-Type-Options"
    ] = "nosniff"

    return response