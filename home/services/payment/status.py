from dataclasses import (
    dataclass,
)
from datetime import (
    date,
    timedelta,
)
from decimal import Decimal

from django.db.models import (
    Sum,
)
from django.utils import (
    timezone,
)

from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentRecord,
)


ZERO = Decimal(
    "0.00"
)


class PaymentState:
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    WAIVED = "waived"


class TimingState:
    UPCOMING = "upcoming"
    DUE_TODAY = "due_today"

    GRACE_PERIOD = (
        "grace_period"
    )

    OVERDUE = "overdue"

    AWAITING_MILESTONE = (
        "awaiting_milestone"
    )

    SETTLED = "settled"


@dataclass(
    frozen=True,
    slots=True,
)
class InstallmentFinancialStatus:
    expected_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal

    payment_state: str
    timing_state: str

    effective_due_date: date | None


@dataclass(
    frozen=True,
    slots=True,
)
class AgreementFinancialSummary:
    total_amount: Decimal

    scheduled_amount: Decimal

    received_amount: Decimal

    allocated_amount: Decimal

    unallocated_amount: Decimal

    outstanding_amount: Decimal

    overpaid_amount: Decimal

    waived_amount: Decimal


def _sum_amount(
    queryset,
) -> Decimal:
    return (
        queryset.aggregate(
            total=Sum(
                "amount"
            ),
        )[
            "total"
        ]
        or ZERO
    )


def get_installment_paid_amount(
    installment:
        PaymentInstallment,
) -> Decimal:
    return _sum_amount(
        PaymentAllocation
        .objects
        .filter(
            installment=(
                installment
            ),
            payment__status=(
                PaymentRecord
                .Status
                .POSTED
            ),
        )
    )


def get_installment_status(
    installment:
        PaymentInstallment,
    *,
    on_date:
        date | None = None,
    paid_amount:
        Decimal | None = None,
) -> InstallmentFinancialStatus:
    today = (
        on_date
        or timezone.localdate()
    )

    paid = (
        paid_amount
        if paid_amount is not None
        else (
            get_installment_paid_amount(
                installment
            )
        )
    )

    if installment.is_waived:
        payment_state = (
            PaymentState.WAIVED
        )

        outstanding = ZERO

    elif (
        paid
        >= installment.amount
    ):
        payment_state = (
            PaymentState.PAID
        )

        outstanding = ZERO

    elif paid > 0:
        payment_state = (
            PaymentState.PARTIAL
        )

        outstanding = (
            installment.amount
            - paid
        )

    else:
        payment_state = (
            PaymentState.UNPAID
        )

        outstanding = (
            installment.amount
        )

    effective_due_date = (
        installment.due_date
        or installment
        .expected_due_date
    )

    if payment_state in (
        PaymentState.PAID,
        PaymentState.WAIVED,
    ):
        timing_state = (
            TimingState.SETTLED
        )

    elif (
        installment.due_type
        == PaymentInstallment
        .DueType.MILESTONE
        and installment
        .due_date is None
    ):
        timing_state = (
            TimingState
            .AWAITING_MILESTONE
        )

    elif (
        today
        < effective_due_date
    ):
        timing_state = (
            TimingState.UPCOMING
        )

    elif (
        today
        == effective_due_date
    ):
        timing_state = (
            TimingState.DUE_TODAY
        )

    else:
        grace_until = (
            effective_due_date
            + timedelta(
                days=(
                    installment
                    .grace_period_days
                )
            )
        )

        if (
            installment
            .grace_period_days > 0
            and today
            <= grace_until
        ):
            timing_state = (
                TimingState
                .GRACE_PERIOD
            )

        else:
            timing_state = (
                TimingState.OVERDUE
            )

    return (
        InstallmentFinancialStatus(
            expected_amount=(
                installment.amount
            ),
            paid_amount=paid,
            outstanding_amount=(
                outstanding
            ),
            payment_state=(
                payment_state
            ),
            timing_state=(
                timing_state
            ),
            effective_due_date=(
                effective_due_date
            ),
        )
    )


def get_agreement_summary(
    agreement:
        PaymentAgreement,
) -> AgreementFinancialSummary:
    received = _sum_amount(
        PaymentRecord
        .objects
        .filter(
            agreement=agreement,
            status=(
                PaymentRecord
                .Status.POSTED
            ),
        )
    )

    scheduled = _sum_amount(
        PaymentInstallment
        .objects
        .filter(
            agreement=agreement,
        )
    )

    allocated = _sum_amount(
        PaymentAllocation
        .objects
        .filter(
            installment__agreement=(
                agreement
            ),
            payment__status=(
                PaymentRecord
                .Status.POSTED
            ),
        )
    )

    waived = _sum_amount(
        PaymentInstallment
        .objects
        .filter(
            agreement=agreement,
            is_waived=True,
        )
    )

    outstanding = max(
        agreement.total_amount
        - received
        - waived,
        ZERO,
    )

    overpaid = max(
        received
        + waived
        - agreement.total_amount,
        ZERO,
    )

    unallocated = max(
        received
        - allocated,
        ZERO,
    )

    return (
        AgreementFinancialSummary(
            total_amount=(
                agreement
                .total_amount
            ),
            scheduled_amount=(
                scheduled
            ),
            received_amount=(
                received
            ),
            allocated_amount=(
                allocated
            ),
            unallocated_amount=(
                unallocated
            ),
            outstanding_amount=(
                outstanding
            ),
            overpaid_amount=(
                overpaid
            ),
            waived_amount=(
                waived
            ),
        )
    )