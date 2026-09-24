from datetime import date

from django.db.models import Q

from home.models import (
    PaymentAgreement,
    PaymentRecord,
)


AGREEMENT_ORDERINGS = {
    "title",
    "-title",
    "total_amount",
    "-total_amount",
    "agreement_date",
    "-agreement_date",
    "start_date",
    "-start_date",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
}


RECORD_ORDERINGS = {
    "amount",
    "-amount",
    "paid_at",
    "-paid_at",
    "created_at",
    "-created_at",
}


class PaymentFilterError(
    ValueError
):
    pass


def apply_agreement_filters(
    queryset,
    query_params,
):
    search = (
        query_params.get(
            "search",
            "",
        ).strip()
    )

    ordering = (
        query_params.get(
            "ordering",
            "-created_at",
        ).strip()
    )

    if (
        ordering
        not in AGREEMENT_ORDERINGS
    ):
        raise PaymentFilterError(
            "Invalid ordering."
        )

    if search:
        queryset = queryset.filter(
            Q(
                title__icontains=(
                    search
                )
            )
            | Q(
                reference__icontains=(
                    search
                )
            )
            | Q(
                portfolio__name__icontains=(
                    search
                )
            )
        )

    portfolio_id = (
        _positive_integer(
            query_params.get(
                "portfolio_id"
            ),
            "portfolio_id",
        )
    )

    if portfolio_id:
        queryset = queryset.filter(
            portfolio_id=(
                portfolio_id
            )
        )

    queryset = _choice_filter(
        queryset,
        query_params,
        "agreement_type",
        (
            PaymentAgreement
            .AgreementType
            .values
        ),
    )

    queryset = _choice_filter(
        queryset,
        query_params,
        "status",
        (
            PaymentAgreement
            .Status
            .values
        ),
    )

    queryset = _choice_filter(
        queryset,
        query_params,
        "currency",
        (
            PaymentAgreement
            .Currency
            .values
        ),
    )

    return queryset.order_by(
        ordering,
        "pk",
    )


def apply_record_filters(
    queryset,
    query_params,
):
    ordering = (
        query_params.get(
            "ordering",
            "-paid_at",
        ).strip()
    )

    if (
        ordering
        not in RECORD_ORDERINGS
    ):
        raise PaymentFilterError(
            "Invalid ordering."
        )

    agreement_id = (
        _positive_integer(
            query_params.get(
                "agreement_id"
            ),
            "agreement_id",
        )
    )

    portfolio_id = (
        _positive_integer(
            query_params.get(
                "portfolio_id"
            ),
            "portfolio_id",
        )
    )

    if agreement_id:
        queryset = queryset.filter(
            agreement_id=(
                agreement_id
            )
        )

    if portfolio_id:
        queryset = queryset.filter(
            agreement__portfolio_id=(
                portfolio_id
            )
        )

    queryset = _choice_filter(
        queryset,
        query_params,
        "status",
        PaymentRecord.Status.values,
    )

    queryset = _choice_filter(
        queryset,
        query_params,
        "payment_method",
        PaymentRecord.Method.values,
    )

    paid_from = _date_value(
        query_params.get(
            "paid_from"
        ),
        "paid_from",
    )

    paid_to = _date_value(
        query_params.get(
            "paid_to"
        ),
        "paid_to",
    )

    if paid_from:
        queryset = queryset.filter(
            paid_at__date__gte=(
                paid_from
            )
        )

    if paid_to:
        queryset = queryset.filter(
            paid_at__date__lte=(
                paid_to
            )
        )

    return queryset.order_by(
        ordering,
        "pk",
    )


def _choice_filter(
    queryset,
    params,
    field,
    choices,
):
    value = params.get(
        field
    )

    if not value:
        return queryset

    if value not in choices:
        raise PaymentFilterError(
            f"Invalid {field}."
        )

    return queryset.filter(
        **{
            field: value,
        }
    )


def _positive_integer(
    value,
    field,
):
    if value in (
        None,
        "",
    ):
        return None

    try:
        parsed = int(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        raise PaymentFilterError(
            f"{field} must be a "
            "positive integer."
        )

    if parsed < 1:
        raise PaymentFilterError(
            f"{field} must be a "
            "positive integer."
        )

    return parsed


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
    except ValueError:
        raise PaymentFilterError(
            f"{field} must use "
            "YYYY-MM-DD."
        )