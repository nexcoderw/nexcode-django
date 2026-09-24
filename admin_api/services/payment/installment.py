from decimal import Decimal

from django.db import (
    models,
    transaction,
)
from django.utils import timezone

from admin_api.forms.payment.installment import (
    INSTALLMENT_FIELDS,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from home.models import (
    PaymentAllocation,
    PaymentAgreement,
    PaymentInstallment,
    PaymentRecord,
)


ZERO = Decimal("0.00")


@transaction.atomic
def create_installment(
    agreement,
    cleaned_data,
):
    """
    Create one installment for an agreement.

    The agreement is locked while the installment is created so two
    concurrent requests cannot independently push the schedule beyond
    the agreement total.
    """

    agreement = (
        PaymentAgreement.objects
        .select_for_update()
        .get(
            pk=agreement.pk,
        )
    )

    _assert_mutable_agreement(
        agreement
    )

    installment = PaymentInstallment(
        agreement=agreement,
        sequence=(
            cleaned_data[
                "sequence"
            ]
        ),
        title=(
            cleaned_data[
                "title"
            ]
        ),
        installment_type=(
            cleaned_data[
                "installment_type"
            ]
        ),
        amount=(
            cleaned_data[
                "amount"
            ]
        ),
        due_type=(
            cleaned_data[
                "due_type"
            ]
        ),
        expected_due_date=(
            cleaned_data[
                "expected_due_date"
            ]
        ),
        due_date=(
            cleaned_data.get(
                "due_date"
            )
        ),
        milestone=(
            cleaned_data.get(
                "milestone"
            )
            or ""
        ),
        grace_period_days=(
            cleaned_data.get(
                "grace_period_days"
            )
            or 0
        ),
        notes=(
            cleaned_data.get(
                "notes"
            )
            or ""
        ),
    )

    _assert_schedule_total(
        agreement,
        installment.amount,
    )

    installment.full_clean()
    installment.save()

    return installment


@transaction.atomic
def update_installment(
    installment,
    form,
):
    """
    Modify an existing installment without allowing financial history
    or the agreement total to become inconsistent.
    """

    installment = (
        PaymentInstallment.objects
        .select_for_update()
        .select_related(
            "agreement"
        )
        .get(
            pk=installment.pk,
        )
    )

    _assert_mutable_agreement(
        installment.agreement
    )

    data = form.cleaned_data

    for field_name in (
        INSTALLMENT_FIELDS
    ):
        if field_name not in form.data:
            continue

        value = data.get(
            field_name
        )

        if field_name in (
            "milestone",
            "notes",
        ):
            value = value or ""

        if (
            field_name
            == "grace_period_days"
        ):
            value = value or 0

        setattr(
            installment,
            field_name,
            value,
        )

    allocated_amount = (
        _posted_allocated_amount(
            installment
        )
    )

    if (
        installment.amount
        < allocated_amount
    ):
        raise PaymentOperationError(
            (
                "Installment amount "
                "cannot be lower than "
                "the amount already "
                "paid."
            ),
            field="amount",
        )

    _assert_schedule_total(
        installment.agreement,
        installment.amount,
        exclude_id=(
            installment.pk
        ),
    )

    installment.full_clean()
    installment.save()

    return installment


@transaction.atomic
def delete_installment(
    installment,
):
    """
    Delete an installment only when it has no financial history.
    """

    installment = (
        PaymentInstallment.objects
        .select_for_update()
        .select_related(
            "agreement"
        )
        .get(
            pk=installment.pk,
        )
    )

    _assert_mutable_agreement(
        installment.agreement
    )

    if (
        installment.allocations
        .exists()
    ):
        raise PaymentOperationError(
            (
                "An installment with "
                "payment history cannot "
                "be deleted."
            )
        )

    installment.delete()


@transaction.atomic
def confirm_milestone(
    installment,
    due_date,
):
    """
    Give a milestone installment its confirmed due date.

    The forecast date remains unchanged so the system can later compare
    the estimated milestone date with the confirmed date.
    """

    installment = (
        PaymentInstallment.objects
        .select_for_update()
        .get(
            pk=installment.pk,
        )
    )

    _assert_mutable_agreement(
        installment.agreement
    )

    if (
        installment.due_type
        != (
            PaymentInstallment
            .DueType
            .MILESTONE
        )
    ):
        raise PaymentOperationError(
            (
                "Only milestone "
                "installments can "
                "receive a confirmed "
                "milestone date."
            )
        )

    installment.due_date = (
        due_date
    )

    installment.full_clean()

    installment.save(
        update_fields=(
            "due_date",
            "updated_at",
        )
    )

    return installment


@transaction.atomic
def waive_installment(
    installment,
    reason,
):
    """
    Waive an unpaid installment while retaining it in the financial
    history.

    Any posted allocation prevents a waiver because received money
    should be reconciled before the obligation can be waived.
    """

    installment = (
        PaymentInstallment.objects
        .select_for_update()
        .select_related(
            "agreement"
        )
        .get(
            pk=installment.pk,
        )
    )

    _assert_mutable_agreement(
        installment.agreement
    )

    if installment.is_waived:
        raise PaymentOperationError(
            (
                "Installment is "
                "already waived."
            )
        )

    if (
        _posted_allocated_amount(
            installment
        )
        > ZERO
    ):
        raise PaymentOperationError(
            (
                "A paid or partially "
                "paid installment "
                "cannot be waived."
            )
        )

    reason = reason.strip()

    if not reason:
        raise PaymentOperationError(
            (
                "A waiver reason "
                "is required."
            ),
            field="reason",
        )

    installment.is_waived = True
    installment.waived_at = (
        timezone.now()
    )
    installment.waiver_reason = (
        reason
    )

    installment.full_clean()

    installment.save(
        update_fields=(
            "is_waived",
            "waived_at",
            "waiver_reason",
            "updated_at",
        )
    )

    return installment


def _assert_mutable_agreement(
    agreement,
):
    """
    Completed and cancelled agreements are historical records and may
    no longer have their installment structure modified.
    """

    if agreement.status in (
        PaymentAgreement
        .Status.COMPLETED,
        PaymentAgreement
        .Status.CANCELLED,
    ):
        raise PaymentOperationError(
            (
                "Installments cannot "
                "be modified on a "
                "completed or "
                "cancelled agreement."
            )
        )


def _assert_schedule_total(
    agreement,
    amount,
    *,
    exclude_id=None,
):
    """
    Ensure the installment schedule never exceeds the commercial value
    recorded on the agreement.
    """

    queryset = (
        agreement
        .installments
        .all()
    )

    if exclude_id is not None:
        queryset = queryset.exclude(
            pk=exclude_id,
        )

    existing_total = (
        queryset.aggregate(
            total=models.Sum(
                "amount"
            ),
        )[
            "total"
        ]
        or ZERO
    )

    if (
        existing_total
        + amount
        > agreement.total_amount
    ):
        raise PaymentOperationError(
            (
                "Installment schedule "
                "cannot exceed the "
                "agreement total."
            ),
            field="amount",
        )


def _posted_allocated_amount(
    installment,
):
    """
    Return money allocated to this installment from transactions that
    remain posted. Voided payments do not count toward the paid amount.
    """

    return (
        PaymentAllocation.objects
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
        .aggregate(
            total=models.Sum(
                "amount"
            ),
        )[
            "total"
        ]
        or ZERO
    )