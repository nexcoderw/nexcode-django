from datetime import date, datetime
from decimal import Decimal


def serialize_payment_report(
    value,
):
    if isinstance(
        value,
        Decimal,
    ):
        return str(value)

    if isinstance(
        value,
        (
            date,
            datetime,
        ),
    ):
        return value.isoformat()

    if isinstance(
        value,
        dict,
    ):
        return {
            key:
                serialize_payment_report(
                    item
                )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (list, tuple),
    ):
        return [
            serialize_payment_report(
                item
            )
            for item
            in value
        ]

    return value