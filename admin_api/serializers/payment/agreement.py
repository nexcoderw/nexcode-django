def serialize_agreement(
    agreement,
):
    return {
        "id":
            agreement.pk,

        "portfolio": {
            "id":
                agreement
                .portfolio_id,

            "name":
                agreement
                .portfolio
                .name,

            "slug":
                agreement
                .portfolio
                .slug,
        },

        "title":
            agreement.title,

        "reference":
            agreement.reference
            or None,

        "agreement_type":
            agreement
            .agreement_type,

        "currency":
            agreement.currency,

        "total_amount":
            str(
                agreement
                .total_amount
            ),

        "agreement_date":
            _value(
                agreement
                .agreement_date
            ),

        "start_date":
            _value(
                agreement
                .start_date
            ),

        "end_date":
            _value(
                agreement
                .end_date
            ),

        "status":
            agreement.status,

        "notes":
            agreement.notes,

        "created_at":
            _value(
                agreement
                .created_at
            ),

        "updated_at":
            _value(
                agreement
                .updated_at
            ),
    }


def _value(
    value,
):
    return (
        value.isoformat()
        if value
        else None
    )