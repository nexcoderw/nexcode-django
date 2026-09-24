def serialize_payment_record(
    payment,
):
    return {
        "id":
            payment.pk,

        "agreement_id":
            payment.agreement_id,

        "amount":
            str(
                payment.amount
            ),

        "currency":
            payment.currency,

        "paid_at":
            payment
            .paid_at
            .isoformat(),

        "payment_method":
            payment
            .payment_method,

        "reference":
            payment.reference
            or None,

        "notes":
            payment.notes,

        "status":
            payment.status,

        "voided_at":
            (
                payment
                .voided_at
                .isoformat()
                if payment
                .voided_at
                else None
            ),

        "void_reason":
            payment.void_reason
            or None,

        "recorded_by": (
            {
                "id":
                    payment
                    .recorded_by_id,

                "name":
                    payment
                    .recorded_by
                    .get_username(),
            }
            if payment
            .recorded_by_id
            else None
        ),

        "allocations": [
            {
                "id":
                    allocation.pk,

                "installment_id":
                    allocation
                    .installment_id,

                "installment_title":
                    allocation
                    .installment
                    .title,

                "amount":
                    str(
                        allocation
                        .amount
                    ),
            }
            for allocation
            in payment
            .allocations
            .all()
        ],

        "created_at":
            payment
            .created_at
            .isoformat(),

        "updated_at":
            payment
            .updated_at
            .isoformat(),
    }