def serialize_agreement_summary(
    summary,
):
    return {
        "total_amount":
            str(
                summary
                .total_amount
            ),

        "scheduled_amount":
            str(
                summary
                .scheduled_amount
            ),

        "received_amount":
            str(
                summary
                .received_amount
            ),

        "allocated_amount":
            str(
                summary
                .allocated_amount
            ),

        "unallocated_amount":
            str(
                summary
                .unallocated_amount
            ),

        "outstanding_amount":
            str(
                summary
                .outstanding_amount
            ),

        "overpaid_amount":
            str(
                summary
                .overpaid_amount
            ),

        "waived_amount":
            str(
                summary
                .waived_amount
            ),
    }


def serialize_portfolio_summary(
    summary,
):
    return {
        "total_contracted":
            str(
                summary[
                    "total_contracted"
                ]
            ),

        "total_received":
            str(
                summary[
                    "total_received"
                ]
            ),

        "outstanding":
            str(
                summary[
                    "outstanding"
                ]
            ),

        "overdue":
            str(
                summary[
                    "overdue"
                ]
            ),

        "agreement_count":
            summary[
                "agreement_count"
            ],
    }