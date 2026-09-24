from decimal import Decimal

from django.db import transaction

from admin_api.services.payment import (
    PaymentOperationError,
)
from home.models import (
    PaymentAgreement,
)
from home.services.payment.schedule import (
    build_contract_schedule,
    build_maintenance_schedule,
    create_installment_schedule,
)


@transaction.atomic
def create_contract_schedule(
    agreement,
    cleaned_data,
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
        agreement.agreement_type
        == (
            PaymentAgreement
            .AgreementType
            .MAINTENANCE
        )
    ):
        raise (
            PaymentOperationError(
                "Use a maintenance "
                "schedule for a "
                "maintenance agreement."
            )
        )

    schedule = (
        build_contract_schedule(
            total_amount=(
                agreement.total_amount
            ),
            down_payment_amount=(
                cleaned_data.get(
                    "down_payment_amount"
                )
                or Decimal(
                    "0.00"
                )
            ),
            down_payment_date=(
                cleaned_data.get(
                    "down_payment_date"
                )
            ),
            installment_count=(
                cleaned_data.get(
                    "installment_count"
                )
                or 0
            ),
            first_installment_date=(
                cleaned_data.get(
                    "first_installment_date"
                )
            ),
            grace_period_days=(
                cleaned_data.get(
                    "grace_period_days"
                )
                or 0
            ),
        )
    )

    return (
        create_installment_schedule(
            agreement,
            schedule,
        )
    )


@transaction.atomic
def create_maintenance_schedule(
    agreement,
    cleaned_data,
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
        agreement.agreement_type
        != (
            PaymentAgreement
            .AgreementType
            .MAINTENANCE
        )
    ):
        raise (
            PaymentOperationError(
                (
                    "Maintenance "
                    "schedules require "
                    "a maintenance "
                    "agreement."
                )
            )
        )

    schedule = (
        build_maintenance_schedule(
            monthly_amount=(
                cleaned_data[
                    "monthly_amount"
                ]
            ),
            months=(
                cleaned_data[
                    "months"
                ]
            ),
            first_due_date=(
                cleaned_data[
                    "first_due_date"
                ]
            ),
            grace_period_days=(
                cleaned_data.get(
                    "grace_period_days"
                )
                or 0
            ),
        )
    )

    return (
        create_installment_schedule(
            agreement,
            schedule,
        )
    )