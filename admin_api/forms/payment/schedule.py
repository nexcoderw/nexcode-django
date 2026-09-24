from decimal import Decimal

from django import forms


class ContractScheduleForm(
    forms.Form
):
    down_payment_amount = (
        forms.DecimalField(
            max_digits=18,
            decimal_places=2,
            min_value=Decimal(
                "0.00"
            ),
            required=False,
        )
    )

    down_payment_date = (
        forms.DateField(
            required=False,
        )
    )

    installment_count = (
        forms.IntegerField(
            min_value=0,
            required=False,
        )
    )

    first_installment_date = (
        forms.DateField(
            required=False,
        )
    )

    grace_period_days = (
        forms.IntegerField(
            min_value=0,
            required=False,
        )
    )

    def clean(self):
        data = super().clean()

        down_payment = (
            data.get(
                "down_payment_amount"
            )
            or Decimal(
                "0.00"
            )
        )

        installments = (
            data.get(
                "installment_count"
            )
            or 0
        )

        if (
            down_payment > 0
            and not data.get(
                "down_payment_date"
            )
        ):
            self.add_error(
                "down_payment_date",
                (
                    "Down payment date "
                    "is required."
                ),
            )

        if (
            installments > 0
            and not data.get(
                "first_installment_date"
            )
        ):
            self.add_error(
                "first_installment_date",
                (
                    "First installment "
                    "date is required."
                ),
            )

        return data


class MaintenanceScheduleForm(
    forms.Form
):
    monthly_amount = (
        forms.DecimalField(
            max_digits=18,
            decimal_places=2,
            min_value=Decimal(
                "0.01"
            ),
        )
    )

    months = forms.IntegerField(
        min_value=1,
        max_value=120,
    )

    first_due_date = (
        forms.DateField()
    )

    grace_period_days = (
        forms.IntegerField(
            min_value=0,
            required=False,
        )
    )