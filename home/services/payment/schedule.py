from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import (
    Decimal,
    ROUND_DOWN,
)

from django.core.exceptions import (
    ValidationError,
)
from django.db import transaction

from home.models import (
    PaymentAgreement,
    PaymentInstallment,
)


CENT = Decimal(
    "0.01"
)


@dataclass(
    frozen=True,
    slots=True,
)
class InstallmentPlanItem:
    sequence: int
    title: str
    installment_type: str
    amount: Decimal
    due_type: str
    expected_due_date: date

    due_date: date | None = None
    milestone: str = ""
    grace_period_days: int = 0


def normalize_money(
    value: Decimal,
) -> Decimal:
    return value.quantize(
        CENT
    )


def split_amount_evenly(
    total_amount: Decimal,
    count: int,
) -> tuple[
    Decimal,
    ...,
]:
    """Split money without losing cents.

    Any rounding remainder is assigned to
    the final installment.
    """

    total = normalize_money(
        total_amount
    )

    if total <= 0:
        raise ValidationError(
            "Total amount must "
            "be greater than zero."
        )

    if count <= 0:
        raise ValidationError(
            "Installment count must "
            "be greater than zero."
        )

    if (
        total
        < CENT * count
    ):
        raise ValidationError(
            "The amount is too small "
            "for the requested number "
            "of installments."
        )

    regular_amount = (
        total / count
    ).quantize(
        CENT,
        rounding=ROUND_DOWN,
    )

    amounts = [
        regular_amount
        for _ in range(
            count
        )
    ]

    amounts[-1] = (
        total
        - regular_amount
        * (
            count - 1
        )
    )

    return tuple(
        amounts
    )


def add_months(
    value: date,
    months: int,
) -> date:
    """Move a date by calendar months.

    A date such as January 31 becomes
    February 28/29, while later months
    return to day 31 where possible.
    """

    month_index = (
        value.month
        - 1
        + months
    )

    year = (
        value.year
        + month_index // 12
    )

    month = (
        month_index % 12
        + 1
    )

    day = min(
        value.day,
        monthrange(
            year,
            month,
        )[1],
    )

    return date(
        year,
        month,
        day,
    )


def build_monthly_schedule(
    *,
    total_amount: Decimal,
    installment_count: int,
    first_due_date: date,
    start_sequence: int = 1,
    title_prefix: str = (
        "Installment"
    ),
    installment_type: str = (
        PaymentInstallment
        .Type.INSTALLMENT
    ),
    grace_period_days: int = 0,
) -> tuple[
    InstallmentPlanItem,
    ...,
]:
    if start_sequence <= 0:
        raise ValidationError(
            "Schedule sequence must "
            "start above zero."
        )

    amounts = (
        split_amount_evenly(
            total_amount,
            installment_count,
        )
    )

    return tuple(
        InstallmentPlanItem(
            sequence=(
                start_sequence
                + index
            ),
            title=(
                f"{title_prefix} "
                f"{index + 1}"
            ),
            installment_type=(
                installment_type
            ),
            amount=amount,
            due_type=(
                PaymentInstallment
                .DueType
                .FIXED_DATE
            ),
            expected_due_date=(
                add_months(
                    first_due_date,
                    index,
                )
            ),
            due_date=(
                add_months(
                    first_due_date,
                    index,
                )
            ),
            grace_period_days=(
                grace_period_days
            ),
        )
        for index, amount
        in enumerate(
            amounts
        )
    )


def build_contract_schedule(
    *,
    total_amount: Decimal,
    down_payment_amount: Decimal,
    down_payment_date: date,
    installment_count: int,
    first_installment_date:
        date | None,
    grace_period_days: int = 0,
) -> tuple[
    InstallmentPlanItem,
    ...,
]:
    total = normalize_money(
        total_amount
    )

    down_payment = (
        normalize_money(
            down_payment_amount
        )
    )

    if total <= 0:
        raise ValidationError(
            "Contract total must "
            "be greater than zero."
        )

    if down_payment < 0:
        raise ValidationError(
            "Down payment cannot "
            "be negative."
        )

    if down_payment > total:
        raise ValidationError(
            "Down payment cannot "
            "exceed the contract "
            "total."
        )

    items = []

    next_sequence = 1

    if down_payment > 0:
        items.append(
            InstallmentPlanItem(
                sequence=1,
                title=(
                    "Down payment"
                ),
                installment_type=(
                    PaymentInstallment
                    .Type
                    .DOWN_PAYMENT
                ),
                amount=down_payment,
                due_type=(
                    PaymentInstallment
                    .DueType
                    .FIXED_DATE
                ),
                expected_due_date=(
                    down_payment_date
                ),
                due_date=(
                    down_payment_date
                ),
                grace_period_days=(
                    grace_period_days
                ),
            )
        )

        next_sequence = 2

    remaining = (
        total
        - down_payment
    )

    if remaining == 0:
        if installment_count != 0:
            raise ValidationError(
                "No installments are "
                "required when the down "
                "payment covers the "
                "contract total."
            )

        return tuple(
            items
        )

    if installment_count <= 0:
        raise ValidationError(
            "Remaining contract value "
            "requires at least one "
            "installment."
        )

    if (
        first_installment_date
        is None
    ):
        raise ValidationError(
            "The first installment "
            "date is required."
        )

    items.extend(
        build_monthly_schedule(
            total_amount=remaining,
            installment_count=(
                installment_count
            ),
            first_due_date=(
                first_installment_date
            ),
            start_sequence=(
                next_sequence
            ),
            title_prefix=(
                "Installment"
            ),
            installment_type=(
                PaymentInstallment
                .Type
                .INSTALLMENT
            ),
            grace_period_days=(
                grace_period_days
            ),
        )
    )

    return tuple(
        items
    )


def build_maintenance_schedule(
    *,
    monthly_amount: Decimal,
    months: int,
    first_due_date: date,
    grace_period_days: int = 0,
) -> tuple[
    InstallmentPlanItem,
    ...,
]:
    if months <= 0:
        raise ValidationError(
            "Maintenance duration "
            "must be at least one "
            "month."
        )

    amount = normalize_money(
        monthly_amount
    )

    if amount <= 0:
        raise ValidationError(
            "Monthly maintenance "
            "amount must be greater "
            "than zero."
        )

    return (
        build_monthly_schedule(
            total_amount=(
                amount * months
            ),
            installment_count=(
                months
            ),
            first_due_date=(
                first_due_date
            ),
            title_prefix=(
                "Maintenance"
            ),
            installment_type=(
                PaymentInstallment
                .Type
                .MAINTENANCE
            ),
            grace_period_days=(
                grace_period_days
            ),
        )
    )


def build_milestone_item(
    *,
    sequence: int,
    title: str,
    amount: Decimal,
    expected_due_date: date,
    milestone: str,
    installment_type: str = (
        PaymentInstallment
        .Type.MILESTONE
    ),
    confirmed_due_date:
        date | None = None,
    grace_period_days: int = 0,
) -> InstallmentPlanItem:
    if sequence <= 0:
        raise ValidationError(
            "Milestone sequence must "
            "be greater than zero."
        )

    amount = normalize_money(
        amount
    )

    if amount <= 0:
        raise ValidationError(
            "Milestone amount must "
            "be greater than zero."
        )

    milestone = (
        milestone.strip()
    )

    if not milestone:
        raise ValidationError(
            "Milestone name is "
            "required."
        )

    return InstallmentPlanItem(
        sequence=sequence,
        title=title.strip(),
        installment_type=(
            installment_type
        ),
        amount=amount,
        due_type=(
            PaymentInstallment
            .DueType
            .MILESTONE
        ),
        expected_due_date=(
            expected_due_date
        ),
        due_date=(
            confirmed_due_date
        ),
        milestone=milestone,
        grace_period_days=(
            grace_period_days
        ),
    )


@transaction.atomic
def create_installment_schedule(
    agreement: PaymentAgreement,
    items: tuple[
        InstallmentPlanItem,
        ...,
    ],
) -> list[
    PaymentInstallment
]:
    """Persist a complete agreement schedule.

    Existing schedules are never silently
    replaced. Editing an existing schedule
    should be an explicit later operation.
    """

    if not agreement.pk:
        raise ValidationError(
            "Agreement must be saved "
            "before creating its "
            "payment schedule."
        )

    if (
        agreement
        .installments
        .exists()
    ):
        raise ValidationError(
            "This agreement already "
            "has a payment schedule."
        )

    items = tuple(
        items
    )

    if not items:
        raise ValidationError(
            "Payment schedule cannot "
            "be empty."
        )

    sequences = [
        item.sequence
        for item in items
    ]

    if (
        len(sequences)
        != len(
            set(
                sequences
            )
        )
    ):
        raise ValidationError(
            "Payment schedule contains "
            "duplicate sequence "
            "numbers."
        )

    scheduled_total = sum(
        (
            item.amount
            for item in items
        ),
        Decimal(
            "0.00"
        ),
    )

    if (
        normalize_money(
            scheduled_total
        )
        != normalize_money(
            agreement.total_amount
        )
    ):
        raise ValidationError(
            "Payment schedule total "
            "must equal the agreement "
            "total."
        )

    installments = [
        PaymentInstallment(
            agreement=agreement,
            sequence=(
                item.sequence
            ),
            title=item.title,
            installment_type=(
                item.installment_type
            ),
            amount=item.amount,
            due_type=(
                item.due_type
            ),
            expected_due_date=(
                item
                .expected_due_date
            ),
            due_date=(
                item.due_date
            ),
            milestone=(
                item.milestone
            ),
            grace_period_days=(
                item
                .grace_period_days
            ),
        )
        for item in items
    ]

    for installment in (
        installments
    ):
        installment.full_clean(
            validate_unique=False,
        )

    return (
        PaymentInstallment
        .objects
        .bulk_create(
            installments
        )
    )