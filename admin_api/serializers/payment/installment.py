from home.services.payment.status import (
    get_installment_status,
)


def serialize_installment(
    installment,
):
    paid_amount = getattr(
        installment,
        "posted_paid_amount",
        None,
    )

    financial = (
        get_installment_status(
            installment,
            paid_amount=(
                paid_amount
            ),
        )
    )

    return {
        "id":
            installment.pk,

        "agreement_id":
            installment
            .agreement_id,

        "sequence":
            installment.sequence,

        "title":
            installment.title,

        "installment_type":
            installment
            .installment_type,

        "amount":
            str(
                installment.amount
            ),

        "due_type":
            installment.due_type,

        "expected_due_date":
            (
                installment
                .expected_due_date
                .isoformat()
            ),

        "due_date":
            (
                installment
                .due_date
                .isoformat()
                if installment
                .due_date
                else None
            ),

        "milestone":
            installment.milestone
            or None,

        "grace_period_days":
            installment
            .grace_period_days,

        "is_waived":
            installment.is_waived,

        "waived_at":
            (
                installment
                .waived_at
                .isoformat()
                if installment
                .waived_at
                else None
            ),

        "waiver_reason":
            installment
            .waiver_reason
            or None,

        "notes":
            installment.notes,

        "financial": {
            "expected_amount":
                str(
                    financial
                    .expected_amount
                ),

            "paid_amount":
                str(
                    financial
                    .paid_amount
                ),

            "outstanding_amount":
                str(
                    financial
                    .outstanding_amount
                ),

            "payment_state":
                financial
                .payment_state,

            "timing_state":
                financial
                .timing_state,

            "effective_due_date":
                (
                    financial
                    .effective_due_date
                    .isoformat()
                    if financial
                    .effective_due_date
                    else None
                ),
        },

        "created_at":
            installment
            .created_at
            .isoformat(),

        "updated_at":
            installment
            .updated_at
            .isoformat(),
    }