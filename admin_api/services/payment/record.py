from decimal import Decimal

from django.db import (
    models,
    transaction,
)
from django.utils import timezone

from admin_api.services.payment import (
    PaymentOperationError,
)
from home.models import (
    PaymentAllocation,
    PaymentAgreement,
    PaymentInstallment,
    PaymentRecord,
)


ZERO = Decimal(
    "0.00"
)


@transaction.atomic
def record_payment(
    agreement,
    cleaned_data,
    *,
    recorded_by,
):
    agreement = (
        PaymentAgreement
        .objects
        .select_for_update()
        .get(
            pk=agreement.pk
        )
    )

    if (
        agreement.status
        == (
            PaymentAgreement
            .Status.CANCELLED
        )
    ):
        raise (
            PaymentOperationError(
                "Payments cannot be "
                "recorded against a "
                "cancelled agreement."
            )
        )

    payment = PaymentRecord(
        agreement=agreement,
        amount=(
            cleaned_data[
                "amount"
            ]
        ),
        currency=(
            cleaned_data.get(
                "currency"
            )
            or agreement.currency
        ),
        paid_at=(
            cleaned_data.get(
                "paid_at"
            )
            or timezone.now()
        ),
        payment_method=(
            cleaned_data.get(
                "payment_method"
            )
            or (
                PaymentRecord
                .Method
                .BANK_TRANSFER
            )
        ),
        reference=(
            cleaned_data.get(
                "reference"
            )
            or ""
        ),
        notes=(
            cleaned_data.get(
                "notes"
            )
            or ""
        ),
        recorded_by=(
            recorded_by
        ),
    )

    payment.full_clean()
    payment.save()

    allocations = (
        cleaned_data.get(
            "allocations"
        )
        or []
    )

    if allocations:
        _apply_allocations(
            payment,
            allocations,
        )

    return payment


@transaction.atomic
def allocate_payment(
    payment,
    allocations,
):
    payment = (
        PaymentRecord
        .objects
        .select_for_update()
        .select_related(
            "agreement"
        )
        .get(
            pk=payment.pk
        )
    )

    if (
        payment.status
        != (
            PaymentRecord
            .Status.POSTED
        )
    ):
        raise (
            PaymentOperationError(
                "Voided payments cannot "
                "be allocated."
            )
        )

    _apply_allocations(
        payment,
        allocations,
    )

    return payment


@transaction.atomic
def void_payment(
    payment,
    reason,
):
    payment = (
        PaymentRecord
        .objects
        .select_for_update()
        .get(
            pk=payment.pk
        )
    )

    if (
        payment.status
        == (
            PaymentRecord
            .Status.VOIDED
        )
    ):
        raise (
            PaymentOperationError(
                "Payment is already "
                "voided."
            )
        )

    payment.status = (
        PaymentRecord
        .Status.VOIDED
    )

    payment.voided_at = (
        timezone.now()
    )

    payment.void_reason = (
        reason.strip()
    )

    payment.full_clean()

    payment.save(
        update_fields=(
            "status",
            "voided_at",
            "void_reason",
            "updated_at",
        )
    )

    return payment


def _apply_allocations(
    payment,
    allocations,
):
    installment_ids = {
        item[
            "installment_id"
        ]
        for item
        in allocations
    }

    installments = {
        installment.pk:
            installment
        for installment
        in (
            PaymentInstallment
            .objects
            .select_for_update()
            .filter(
                pk__in=(
                    installment_ids
                )
            )
        )
    }

    if (
        len(installments)
        != len(
            installment_ids
        )
    ):
        raise (
            PaymentOperationError(
                "One or more "
                "installments do not "
                "exist."
            )
        )

    existing_payment_total = (
        PaymentAllocation
        .objects
        .filter(
            payment=payment
        )
        .aggregate(
            total=models.Sum(
                "amount"
            )
        )["total"]
        or ZERO
    )

    request_total = sum(
        (
            item["amount"]
            for item
            in allocations
        ),
        ZERO,
    )

    if (
        existing_payment_total
        + request_total
        > payment.amount
    ):
        raise (
            PaymentOperationError(
                "Allocations cannot "
                "exceed the payment "
                "amount."
            )
        )

    for item in allocations:
        installment = (
            installments[
                item[
                    "installment_id"
                ]
            ]
        )

        if (
            installment
            .agreement_id
            != payment
            .agreement_id
        ):
            raise (
                PaymentOperationError(
                    (
                        "Every allocation "
                        "must belong to "
                        "the same agreement "
                        "as the payment."
                    )
                )
            )

        if installment.is_waived:
            raise (
                PaymentOperationError(
                    (
                        "Waived "
                        "installments "
                        "cannot receive "
                        "payments."
                    )
                )
            )

        posted_total = (
            PaymentAllocation
            .objects
            .filter(
                installment=(
                    installment
                ),
                payment__status=(
                    PaymentRecord
                    .Status.POSTED
                ),
            )
            .aggregate(
                total=models.Sum(
                    "amount"
                )
            )["total"]
            or ZERO
        )

        amount = item[
            "amount"
        ]

        if (
            posted_total + amount
            > installment.amount
        ):
            raise (
                PaymentOperationError(
                    (
                        f"{installment.title} "
                        "would be "
                        "over-allocated."
                    )
                )
            )

        allocation = (
            PaymentAllocation
            .objects
            .select_for_update()
            .filter(
                payment=payment,
                installment=(
                    installment
                ),
            )
            .first()
        )

        if allocation:
            allocation.amount += (
                amount
            )

            allocation.full_clean()
            allocation.save(
                update_fields=(
                    "amount",
                )
            )

        else:
            allocation = (
                PaymentAllocation(
                    payment=payment,
                    installment=(
                        installment
                    ),
                    amount=amount,
                )
            )

            allocation.full_clean()
            allocation.save()