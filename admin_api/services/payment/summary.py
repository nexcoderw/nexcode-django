from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentRecord,
)
from home.services.payment.status import (
    get_installment_status,
)


ZERO = Decimal(
    "0.00"
)


def get_portfolio_financial_summary(
    portfolio,
):
    agreements = list(
        portfolio
        .payment_agreements
        .all()
    )

    agreement_ids = [
        agreement.pk
        for agreement
        in agreements
    ]

    received_by_agreement = {
        row["agreement_id"]:
            row["total"]
        for row
        in (
            PaymentRecord
            .objects
            .filter(
                agreement_id__in=(
                    agreement_ids
                ),
                status=(
                    PaymentRecord
                    .Status.POSTED
                ),
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

    waived_by_agreement = {
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

    total_contracted = ZERO
    total_received = ZERO
    outstanding = ZERO

    for agreement in agreements:
        received = (
            received_by_agreement
            .get(
                agreement.pk,
                ZERO,
            )
        )

        waived = (
            waived_by_agreement
            .get(
                agreement.pk,
                ZERO,
            )
        )

        total_received += (
            received
        )

        if (
            agreement.status
            == (
                PaymentAgreement
                .Status.CANCELLED
            )
        ):
            continue

        total_contracted += (
            agreement.total_amount
        )

        outstanding += max(
            agreement.total_amount
            - received
            - waived,
            ZERO,
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
    )

    paid_by_installment = {
        row["installment_id"]:
            row["total"]
        for row
        in (
            PaymentAllocation
            .objects
            .filter(
                installment_id__in=[
                    item.pk
                    for item
                    in installments
                ],
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

    overdue = ZERO
    today = timezone.localdate()

    for installment in installments:
        status = (
            get_installment_status(
                installment,
                on_date=today,
                paid_amount=(
                    paid_by_installment
                    .get(
                        installment.pk,
                        ZERO,
                    )
                ),
            )
        )

        if (
            status.timing_state
            == "overdue"
        ):
            overdue += (
                status
                .outstanding_amount
            )

    return {
        "total_contracted":
            total_contracted,
        "total_received":
            total_received,
        "outstanding":
            outstanding,
        "overdue":
            overdue,
        "agreement_count":
            len(agreements),
    }