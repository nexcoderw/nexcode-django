from django.core.exceptions import (
    ValidationError,
)
from django.db import transaction

from admin_api.forms.payment.agreement import (
    AGREEMENT_FIELDS,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from home.models import (
    PaymentAgreement,
)
from home.services.payment.status import (
    get_agreement_summary,
)


LOCKED_FIELDS = {
    "portfolio_id",
    "agreement_type",
    "currency",
    "total_amount",
}


def create_agreement(
    cleaned_data,
):
    portfolio = cleaned_data[
        "portfolio_id"
    ]

    agreement = PaymentAgreement(
        portfolio=portfolio,
        title=cleaned_data[
            "title"
        ],
        reference=(
            cleaned_data.get(
                "reference"
            )
            or ""
        ),
        agreement_type=(
            cleaned_data[
                "agreement_type"
            ]
        ),
        currency=(
            cleaned_data[
                "currency"
            ]
        ),
        total_amount=(
            cleaned_data[
                "total_amount"
            ]
        ),
        agreement_date=(
            cleaned_data[
                "agreement_date"
            ]
        ),
        start_date=(
            cleaned_data[
                "start_date"
            ]
        ),
        end_date=(
            cleaned_data.get(
                "end_date"
            )
        ),
        status=(
            cleaned_data.get(
                "status"
            )
            or (
                PaymentAgreement
                .Status.DRAFT
            )
        ),
        notes=(
            cleaned_data.get(
                "notes"
            )
            or ""
        ),
    )

    agreement.full_clean()

    with transaction.atomic():
        agreement.save()

    return agreement


@transaction.atomic
def update_agreement(
    agreement,
    form,
):
    agreement = (
        PaymentAgreement
        .objects
        .select_for_update()
        .get(
            pk=agreement.pk
        )
    )

    has_financial_activity = (
        agreement
        .installments
        .exists()
        or agreement
        .payments
        .exists()
    )

    if has_financial_activity:
        attempted = (
            set(form.data.keys())
            & LOCKED_FIELDS
        )

        if attempted:
            raise (
                PaymentOperationError(
                    (
                        "Portfolio, type, "
                        "currency and total "
                        "cannot change after "
                        "financial activity "
                        "has started."
                    )
                )
            )

    data = form.cleaned_data

    for field in (
        AGREEMENT_FIELDS
    ):
        if field not in form.data:
            continue

        value = data.get(
            field
        )

        if field == "portfolio_id":
            agreement.portfolio = value

        elif field in (
            "reference",
            "notes",
        ):
            setattr(
                agreement,
                field,
                value or "",
            )

        else:
            setattr(
                agreement,
                field,
                value,
            )

    agreement.full_clean()

    if (
        agreement.status
        == (
            PaymentAgreement
            .Status.COMPLETED
        )
    ):
        summary = (
            get_agreement_summary(
                agreement
            )
        )

        if (
            summary
            .outstanding_amount
            > 0
        ):
            raise (
                PaymentOperationError(
                    (
                        "An agreement with "
                        "an outstanding "
                        "balance cannot be "
                        "completed."
                    ),
                    field="status",
                )
            )

    agreement.save()

    return agreement


@transaction.atomic
def delete_agreement(
    agreement,
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
        != (
            PaymentAgreement
            .Status.DRAFT
        )
    ):
        raise (
            PaymentOperationError(
                "Only draft agreements "
                "can be deleted."
            )
        )

    if (
        agreement
        .payments
        .exists()
    ):
        raise (
            PaymentOperationError(
                "An agreement with "
                "recorded payments "
                "cannot be deleted."
            )
        )

    agreement.delete()