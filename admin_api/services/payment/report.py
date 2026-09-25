from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from django.db.models import (
    Count,
    Sum,
)
from django.db.models.functions import (
    TruncMonth,
)
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentRecord,
    Portfolio,
)
from home.services.payment.status import (
    TimingState,
    get_agreement_summary,
    get_installment_status,
)


ZERO = Decimal("0.00")

OUTSTANDING_KINDS = {
    "all",
    "overdue",
    "due_soon",
}


class PaymentReportError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentReportFilters:
    portfolio_id: int | None
    currency: str | None

    date_from: date | None
    date_to: date | None

    as_of: date
    due_within_days: int

    outstanding_kind: str


def parse_payment_report_filters(
    params,
) -> PaymentReportFilters:
    date_from = _date_value(
        params.get("date_from"),
        "date_from",
    )

    date_to = _date_value(
        params.get("date_to"),
        "date_to",
    )

    if (
        date_from
        and date_to
        and date_from > date_to
    ):
        raise PaymentReportError(
            "date_from cannot be "
            "after date_to."
        )

    as_of = (
        _date_value(
            params.get("as_of"),
            "as_of",
        )
        or timezone.localdate()
    )

    portfolio_id = (
        _positive_integer(
            params.get(
                "portfolio_id"
            ),
            "portfolio_id",
        )
    )

    currency = (
        params.get(
            "currency"
        )
        or None
    )

    if (
        currency
        and currency
        not in (
            PaymentAgreement
            .Currency.values
        )
    ):
        raise PaymentReportError(
            "Invalid currency."
        )

    due_within_days = (
        _positive_integer(
            params.get(
                "due_within_days"
            ),
            "due_within_days",
        )
        or 30
    )

    if due_within_days > 365:
        raise PaymentReportError(
            "due_within_days cannot "
            "exceed 365."
        )

    outstanding_kind = (
        params.get(
            "kind",
            "all",
        )
        .strip()
        .lower()
    )

    if (
        outstanding_kind
        not in OUTSTANDING_KINDS
    ):
        raise PaymentReportError(
            "Invalid outstanding "
            "report kind."
        )

    return PaymentReportFilters(
        portfolio_id=portfolio_id,
        currency=currency,
        date_from=date_from,
        date_to=date_to,
        as_of=as_of,
        due_within_days=(
            due_within_days
        ),
        outstanding_kind=(
            outstanding_kind
        ),
    )


def get_report_overview(
    filters:
        PaymentReportFilters,
):
    agreements = list(
        _agreement_queryset(
            filters
        )
    )

    agreement_ids = [
        agreement.pk
        for agreement
        in agreements
    ]

    received = (
        _amounts_by_agreement(
            PaymentRecord.objects.filter(
                agreement_id__in=(
                    agreement_ids
                ),
                status=(
                    PaymentRecord
                    .Status.POSTED
                ),
            )
        )
    )

    waived = {
        row["agreement_id"]:
            row["total"]
        for row
        in (
            PaymentInstallment
            .objects
            .filter(
                agreement_id__in=(
                    agreement_ids
                ),
                is_waived=True,
            )
            .values(
                "agreement_id"
            )
            .annotate(
                total=Sum(
                    "amount"
                )
            )
        )
    }

    rows = {}

    for agreement in agreements:
        row = rows.setdefault(
            agreement.currency,
            _currency_overview(
                agreement.currency
            ),
        )

        row[
            "agreement_count"
        ] += 1

        if (
            agreement.status
            == PaymentAgreement
            .Status.ACTIVE
        ):
            row[
                "active_agreement_count"
            ] += 1

        row[
            "total_received"
        ] += received.get(
            agreement.pk,
            ZERO,
        )

        if (
            agreement.status
            == PaymentAgreement
            .Status.CANCELLED
        ):
            continue

        row[
            "total_contracted"
        ] += agreement.total_amount

        row[
            "outstanding"
        ] += max(
            agreement.total_amount
            - received.get(
                agreement.pk,
                ZERO,
            )
            - waived.get(
                agreement.pk,
                ZERO,
            ),
            ZERO,
        )

    _apply_installment_position(
        rows,
        agreement_ids,
        filters,
    )

    return {
        "as_of":
            filters.as_of,

        "due_within_days":
            filters.due_within_days,

        "currencies": [
            rows[currency]
            for currency
            in sorted(rows)
        ],
    }


def get_collections_report(
    filters:
        PaymentReportFilters,
):
    queryset = (
        PaymentRecord.objects
        .filter(
            status=(
                PaymentRecord
                .Status.POSTED
            )
        )
    )

    if filters.portfolio_id:
        queryset = queryset.filter(
            agreement__portfolio_id=(
                filters.portfolio_id
            )
        )

    if filters.currency:
        queryset = queryset.filter(
            currency=(
                filters.currency
            )
        )

    if filters.date_from:
        queryset = queryset.filter(
            paid_at__date__gte=(
                filters.date_from
            )
        )

    if filters.date_to:
        queryset = queryset.filter(
            paid_at__date__lte=(
                filters.date_to
            )
        )

    rows = (
        queryset
        .annotate(
            month=TruncMonth(
                "paid_at"
            )
        )
        .values(
            "month",
            "currency",
        )
        .annotate(
            amount=Sum(
                "amount"
            ),
            payment_count=Count(
                "pk"
            ),
        )
        .order_by(
            "month",
            "currency",
        )
    )

    return {
        "date_from":
            filters.date_from,

        "date_to":
            filters.date_to,

        "rows": [
            {
                "month":
                    row["month"]
                    .date()
                    .replace(
                        day=1
                    ),

                "currency":
                    row[
                        "currency"
                    ],

                "amount":
                    row[
                        "amount"
                    ]
                    or ZERO,

                "payment_count":
                    row[
                        "payment_count"
                    ],
            }
            for row
            in rows
        ],
    }


def get_outstanding_report(
    filters:
        PaymentReportFilters,
):
    agreement_queryset = (
        _agreement_queryset(
            filters
        )
        .filter(
            status=(
                PaymentAgreement
                .Status.ACTIVE
            )
        )
    )

    agreement_ids = list(
        agreement_queryset
        .values_list(
            "pk",
            flat=True,
        )
    )

    installments = list(
        PaymentInstallment
        .objects
        .filter(
            agreement_id__in=(
                agreement_ids
            ),
            is_waived=False,
        )
        .select_related(
            "agreement",
            "agreement__portfolio",
        )
    )

    paid = (
        _paid_by_installment(
            [
                installment.pk
                for installment
                in installments
            ]
        )
    )

    window_end = (
        filters.as_of
        + timedelta(
            days=(
                filters
                .due_within_days
            )
        )
    )

    rows = []

    for installment in installments:
        status = (
            get_installment_status(
                installment,
                on_date=(
                    filters.as_of
                ),
                paid_amount=(
                    paid.get(
                        installment.pk,
                        ZERO,
                    )
                ),
            )
        )

        if (
            status
            .outstanding_amount
            <= ZERO
        ):
            continue

        if not _include_outstanding(
            status,
            filters,
            window_end,
        ):
            continue

        due_date = (
            status
            .effective_due_date
        )

        rows.append(
            {
                "installment_id":
                    installment.pk,

                "agreement_id":
                    installment
                    .agreement_id,

                "agreement_title":
                    installment
                    .agreement
                    .title,

                "portfolio": {
                    "id":
                        installment
                        .agreement
                        .portfolio_id,

                    "name":
                        installment
                        .agreement
                        .portfolio
                        .name,
                },

                "title":
                    installment.title,

                "currency":
                    installment
                    .agreement
                    .currency,

                "amount":
                    installment.amount,

                "paid_amount":
                    status
                    .paid_amount,

                "outstanding_amount":
                    status
                    .outstanding_amount,

                "due_date":
                    installment
                    .due_date,

                "expected_due_date":
                    installment
                    .expected_due_date,

                "effective_due_date":
                    due_date,

                "payment_state":
                    status
                    .payment_state,

                "timing_state":
                    status
                    .timing_state,

                "days_from_due": (
                    (
                        filters.as_of
                        - due_date
                    ).days
                    if due_date
                    else None
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            row[
                "effective_due_date"
            ]
            or date.max,
            row[
                "installment_id"
            ],
        )
    )

    return {
        "as_of":
            filters.as_of,

        "due_within_days":
            filters.due_within_days,

        "kind":
            filters
            .outstanding_kind,

        "rows":
            rows,
    }


def get_portfolio_statement(
    portfolio:
        Portfolio,
):
    agreements = list(
        portfolio
        .payment_agreements
        .all()
        .order_by(
            "start_date",
            "pk",
        )
    )

    summaries = {}
    agreement_rows = []

    for agreement in agreements:
        financial = (
            get_agreement_summary(
                agreement
            )
        )

        summary = (
            summaries.setdefault(
                agreement.currency,
                {
                    "currency":
                        agreement
                        .currency,

                    "total_contracted":
                        ZERO,

                    "total_received":
                        ZERO,

                    "outstanding":
                        ZERO,
                },
            )
        )

        summary[
            "total_received"
        ] += (
            financial
            .received_amount
        )

        outstanding = (
            ZERO
            if agreement.status
            == PaymentAgreement
            .Status.CANCELLED
            else (
                financial
                .outstanding_amount
            )
        )

        if (
            agreement.status
            != PaymentAgreement
            .Status.CANCELLED
        ):
            summary[
                "total_contracted"
            ] += (
                agreement
                .total_amount
            )

        summary[
            "outstanding"
        ] += outstanding

        agreement_rows.append(
            {
                "id":
                    agreement.pk,

                "title":
                    agreement.title,

                "reference":
                    agreement.reference
                    or None,

                "status":
                    agreement.status,

                "currency":
                    agreement.currency,

                "total_amount":
                    agreement
                    .total_amount,

                "received_amount":
                    financial
                    .received_amount,

                "outstanding_amount":
                    outstanding,

                "start_date":
                    agreement
                    .start_date,

                "end_date":
                    agreement
                    .end_date,
            }
        )

    payments = (
        PaymentRecord.objects
        .filter(
            agreement__portfolio=(
                portfolio
            )
        )
        .select_related(
            "agreement",
        )
        .order_by(
            "paid_at",
            "pk",
        )
    )

    return {
        "generated_at":
            timezone.now(),

        "portfolio": {
            "id":
                portfolio.pk,

            "name":
                portfolio.name,

            "slug":
                portfolio.slug,
        },

        "currencies": [
            summaries[currency]
            for currency
            in sorted(
                summaries
            )
        ],

        "agreements":
            agreement_rows,

        "payments": [
            {
                "id":
                    payment.pk,

                "receipt_number":
                    payment_receipt_number(
                        payment.pk
                    ),

                "agreement_id":
                    payment
                    .agreement_id,

                "agreement_title":
                    payment
                    .agreement
                    .title,

                "currency":
                    payment.currency,

                "amount":
                    payment.amount,

                "paid_at":
                    payment.paid_at,

                "status":
                    payment.status,

                "payment_method":
                    payment
                    .payment_method,

                "reference":
                    payment.reference
                    or None,
            }
            for payment
            in payments
        ],
    }


def get_payment_receipt(
    payment:
        PaymentRecord,
):
    return {
        "receipt_number":
            payment_receipt_number(
                payment.pk
            ),

        "issued_at":
            timezone.now(),

        "portfolio": {
            "id":
                payment
                .agreement
                .portfolio_id,

            "name":
                payment
                .agreement
                .portfolio
                .name,
        },

        "agreement": {
            "id":
                payment
                .agreement_id,

            "title":
                payment
                .agreement
                .title,

            "reference":
                payment
                .agreement
                .reference
                or None,
        },

        "payment": {
            "id":
                payment.pk,

            "amount":
                payment.amount,

            "currency":
                payment.currency,

            "paid_at":
                payment.paid_at,

            "payment_method":
                payment
                .payment_method,

            "reference":
                payment.reference
                or None,

            "status":
                payment.status,

            "voided_at":
                payment
                .voided_at,

            "void_reason":
                payment
                .void_reason
                or None,

            "recorded_by":
                (
                    payment
                    .recorded_by
                    .get_username()
                    if payment
                    .recorded_by_id
                    else None
                ),
        },

        "allocations": [
            {
                "installment_id":
                    allocation
                    .installment_id,

                "installment_title":
                    allocation
                    .installment
                    .title,

                "amount":
                    allocation.amount,
            }
            for allocation
            in payment
            .allocations
            .all()
        ],
    }


def build_portfolio_statement_pdf(
    statement,
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Payment Statement",
        author="NEXCODE LTD",
    )

    styles = (
        getSampleStyleSheet()
    )

    story = [
        Paragraph(
            "NEXCODE LTD",
            styles["Heading2"],
        ),
        Paragraph(
            "Portfolio Payment Statement",
            styles["Heading1"],
        ),
        Spacer(
            1,
            5 * mm,
        ),
        Paragraph(
            escape(
                statement[
                    "portfolio"
                ][
                    "name"
                ]
            ),
            styles["Heading3"],
        ),
        Paragraph(
            (
                "Generated: "
                f"{statement['generated_at']:%d %b %Y %H:%M}"
            ),
            styles["BodyText"],
        ),
        Spacer(
            1,
            5 * mm,
        ),
    ]

    for summary in (
        statement[
            "currencies"
        ]
    ):
        story.extend(
            [
                Paragraph(
                    escape(
                        summary[
                            "currency"
                        ]
                    ),
                    styles[
                        "Heading3"
                    ],
                ),
                _pdf_table(
                    [
                        [
                            "Contracted",
                            "Received",
                            "Outstanding",
                        ],
                        [
                            _money(
                                summary[
                                    "total_contracted"
                                ],
                                summary[
                                    "currency"
                                ],
                            ),
                            _money(
                                summary[
                                    "total_received"
                                ],
                                summary[
                                    "currency"
                                ],
                            ),
                            _money(
                                summary[
                                    "outstanding"
                                ],
                                summary[
                                    "currency"
                                ],
                            ),
                        ],
                    ]
                ),
                Spacer(
                    1,
                    4 * mm,
                ),
            ]
        )

    story.extend(
        [
            Paragraph(
                "Transactions",
                styles["Heading2"],
            ),
            Spacer(
                1,
                2 * mm,
            ),
        ]
    )

    transaction_rows = [
        [
            "Receipt",
            "Date",
            "Agreement",
            "Amount",
            "Status",
        ]
    ]

    transaction_rows.extend(
        [
            [
                payment[
                    "receipt_number"
                ],
                payment[
                    "paid_at"
                ].strftime(
                    "%d %b %Y"
                ),
                payment[
                    "agreement_title"
                ],
                _money(
                    payment[
                        "amount"
                    ],
                    payment[
                        "currency"
                    ],
                ),
                payment[
                    "status"
                ].title(),
            ]
            for payment
            in statement[
                "payments"
            ]
        ]
    )

    if len(
        transaction_rows
    ) == 1:
        transaction_rows.append(
            [
                "—",
                "—",
                "No payments",
                "—",
                "—",
            ]
        )

    story.append(
        _pdf_table(
            transaction_rows,
            repeat_rows=1,
        )
    )

    document.build(
        story
    )

    return buffer.getvalue()


def build_payment_receipt_pdf(
    receipt,
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=(
            receipt[
                "receipt_number"
            ]
        ),
        author="NEXCODE LTD",
    )

    styles = (
        getSampleStyleSheet()
    )

    payment = receipt[
        "payment"
    ]

    story = [
        Paragraph(
            "NEXCODE LTD",
            styles["Heading2"],
        ),
        Paragraph(
            "Payment Receipt",
            styles["Heading1"],
        ),
        Spacer(
            1,
            5 * mm,
        ),
        Paragraph(
            escape(
                receipt[
                    "receipt_number"
                ]
            ),
            styles["Heading3"],
        ),
        Spacer(
            1,
            3 * mm,
        ),
        _pdf_table(
            [
                [
                    "Portfolio",
                    receipt[
                        "portfolio"
                    ][
                        "name"
                    ],
                ],
                [
                    "Agreement",
                    receipt[
                        "agreement"
                    ][
                        "title"
                    ],
                ],
                [
                    "Payment date",
                    payment[
                        "paid_at"
                    ].strftime(
                        "%d %b %Y"
                    ),
                ],
                [
                    "Amount",
                    _money(
                        payment[
                            "amount"
                        ],
                        payment[
                            "currency"
                        ],
                    ),
                ],
                [
                    "Method",
                    payment[
                        "payment_method"
                    ]
                    .replace(
                        "_",
                        " ",
                    )
                    .title(),
                ],
                [
                    "Reference",
                    payment[
                        "reference"
                    ]
                    or "—",
                ],
                [
                    "Status",
                    payment[
                        "status"
                    ].title(),
                ],
            ]
        ),
        Spacer(
            1,
            5 * mm,
        ),
        Paragraph(
            "Allocation",
            styles["Heading2"],
        ),
    ]

    allocation_rows = [
        [
            "Installment",
            "Amount",
        ]
    ]

    allocation_rows.extend(
        [
            [
                allocation[
                    "installment_title"
                ],
                _money(
                    allocation[
                        "amount"
                    ],
                    payment[
                        "currency"
                    ],
                ),
            ]
            for allocation
            in receipt[
                "allocations"
            ]
        ]
    )

    if len(
        allocation_rows
    ) == 1:
        allocation_rows.append(
            [
                "Unallocated payment",
                _money(
                    payment[
                        "amount"
                    ],
                    payment[
                        "currency"
                    ],
                ),
            ]
        )

    story.append(
        _pdf_table(
            allocation_rows,
            repeat_rows=1,
        )
    )

    if (
        payment[
            "status"
        ]
        == PaymentRecord
        .Status.VOIDED
    ):
        story.extend(
            [
                Spacer(
                    1,
                    5 * mm,
                ),
                Paragraph(
                    (
                        "<b>VOIDED:</b> "
                        + escape(
                            payment[
                                "void_reason"
                            ]
                            or ""
                        )
                    ),
                    styles[
                        "BodyText"
                    ],
                ),
            ]
        )

    document.build(
        story
    )

    return buffer.getvalue()


def payment_receipt_number(
    payment_id,
):
    return (
        f"NEX-PAY-"
        f"{payment_id:06d}"
    )


def _agreement_queryset(
    filters,
):
    queryset = (
        PaymentAgreement
        .objects
        .select_related(
            "portfolio"
        )
    )

    if filters.portfolio_id:
        queryset = queryset.filter(
            portfolio_id=(
                filters.portfolio_id
            )
        )

    if filters.currency:
        queryset = queryset.filter(
            currency=(
                filters.currency
            )
        )

    return queryset


def _amounts_by_agreement(
    queryset,
):
    return {
        row["agreement_id"]:
            row["total"]
        for row
        in (
            queryset
            .values(
                "agreement_id"
            )
            .annotate(
                total=Sum(
                    "amount"
                )
            )
        )
    }


def _paid_by_installment(
    installment_ids,
):
    return {
        row["installment_id"]:
            row["total"]
        for row
        in (
            PaymentAllocation
            .objects
            .filter(
                installment_id__in=(
                    installment_ids
                ),
                payment__status=(
                    PaymentRecord
                    .Status.POSTED
                ),
            )
            .values(
                "installment_id"
            )
            .annotate(
                total=Sum(
                    "amount"
                )
            )
        )
    }


def _currency_overview(
    currency,
):
    return {
        "currency":
            currency,

        "total_contracted":
            ZERO,

        "total_received":
            ZERO,

        "outstanding":
            ZERO,

        "overdue":
            ZERO,

        "due_soon":
            ZERO,

        "agreement_count":
            0,

        "active_agreement_count":
            0,
    }


def _apply_installment_position(
    rows,
    agreement_ids,
    filters,
):
    installments = list(
        PaymentInstallment
        .objects
        .filter(
            agreement_id__in=(
                agreement_ids
            ),
            agreement__status=(
                PaymentAgreement
                .Status.ACTIVE
            ),
            is_waived=False,
        )
        .select_related(
            "agreement"
        )
    )

    paid = _paid_by_installment(
        [
            installment.pk
            for installment
            in installments
        ]
    )

    due_soon_end = (
        filters.as_of
        + timedelta(
            days=(
                filters
                .due_within_days
            )
        )
    )

    for installment in installments:
        status = (
            get_installment_status(
                installment,
                on_date=(
                    filters.as_of
                ),
                paid_amount=(
                    paid.get(
                        installment.pk,
                        ZERO,
                    )
                ),
            )
        )

        row = rows.setdefault(
            installment
            .agreement
            .currency,
            _currency_overview(
                installment
                .agreement
                .currency
            ),
        )

        if (
            status.timing_state
            == TimingState.OVERDUE
        ):
            row[
                "overdue"
            ] += (
                status
                .outstanding_amount
            )

        elif (
            status
            .outstanding_amount
            > ZERO
            and status
            .effective_due_date
            and status
            .effective_due_date
            <= due_soon_end
            and status.timing_state
            != TimingState
            .AWAITING_MILESTONE
        ):
            row[
                "due_soon"
            ] += (
                status
                .outstanding_amount
            )


def _include_outstanding(
    status,
    filters,
    window_end,
):
    if (
        filters
        .outstanding_kind
        == "all"
    ):
        return True

    if (
        filters
        .outstanding_kind
        == "overdue"
    ):
        return (
            status.timing_state
            == TimingState.OVERDUE
        )

    return (
        status.timing_state
        in (
            TimingState.UPCOMING,
            TimingState.DUE_TODAY,
            TimingState.GRACE_PERIOD,
        )
        and status
        .effective_due_date
        is not None
        and status
        .effective_due_date
        <= window_end
    )


def _date_value(
    value,
    field,
):
    if not value:
        return None

    try:
        return date.fromisoformat(
            value
        )
    except ValueError as error:
        raise PaymentReportError(
            f"{field} must use "
            "YYYY-MM-DD."
        ) from error


def _positive_integer(
    value,
    field,
):
    if not value:
        return None

    try:
        parsed = int(value)
    except (
        TypeError,
        ValueError,
    ) as error:
        raise PaymentReportError(
            f"{field} must be a "
            "positive integer."
        ) from error

    if parsed < 1:
        raise PaymentReportError(
            f"{field} must be a "
            "positive integer."
        )

    return parsed


def _money(
    amount,
    currency,
):
    return (
        f"{amount:,.2f} "
        f"{currency}"
    )


def _pdf_table(
    data,
    *,
    repeat_rows=0,
):
    table = Table(
        data,
        repeatRows=(
            repeat_rows
        ),
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#1E1D1E"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor(
                        "#D0D0D0"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return table