from decimal import (
    Decimal,
    InvalidOperation,
)

from django import forms

from home.models import (
    PaymentAgreement,
    PaymentRecord,
)


class AllocationListField(
    forms.Field
):
    def clean(
        self,
        value,
    ):
        value = super().clean(
            value
        )

        if value in (
            None,
            "",
        ):
            return []

        if not isinstance(
            value,
            list,
        ):
            raise (
                forms.ValidationError(
                    "Allocations must "
                    "be a list."
                )
            )

        result = []
        installment_ids = set()

        for item in value:
            if not isinstance(
                item,
                dict,
            ):
                raise (
                    forms.ValidationError(
                        "Each allocation "
                        "must be an object."
                    )
                )

            installment_id = (
                item.get(
                    "installment_id"
                )
            )

            if (
                isinstance(
                    installment_id,
                    bool,
                )
                or not isinstance(
                    installment_id,
                    int,
                )
                or installment_id < 1
            ):
                raise (
                    forms.ValidationError(
                        "Each allocation "
                        "requires a valid "
                        "installment_id."
                    )
                )

            if (
                installment_id
                in installment_ids
            ):
                raise (
                    forms.ValidationError(
                        "An installment "
                        "cannot appear "
                        "twice in one "
                        "allocation "
                        "request."
                    )
                )

            try:
                amount = Decimal(
                    str(
                        item.get(
                            "amount"
                        )
                    )
                ).quantize(
                    Decimal(
                        "0.01"
                    )
                )
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):
                raise (
                    forms.ValidationError(
                        "Allocation amount "
                        "must be valid "
                        "money."
                    )
                )

            if amount <= 0:
                raise (
                    forms.ValidationError(
                        "Allocation amount "
                        "must be greater "
                        "than zero."
                    )
                )

            installment_ids.add(
                installment_id
            )

            result.append(
                {
                    "installment_id":
                        installment_id,
                    "amount":
                        amount,
                }
            )

        return result


class PaymentRecordCreateForm(
    forms.Form
):
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal(
            "0.01"
        ),
    )

    currency = forms.ChoiceField(
        choices=(
            PaymentAgreement
            .Currency
            .choices
        ),
        required=False,
    )

    paid_at = (
        forms.DateTimeField(
            required=False,
        )
    )

    payment_method = (
        forms.ChoiceField(
            choices=(
                PaymentRecord
                .Method
                .choices
            ),
            required=False,
        )
    )

    reference = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    notes = forms.CharField(
        required=False,
        strip=True,
    )

    allocations = (
        AllocationListField(
            required=False,
        )
    )


class PaymentAllocationForm(
    forms.Form
):
    allocations = (
        AllocationListField()
    )

    def clean_allocations(
        self,
    ):
        allocations = (
            self.cleaned_data[
                "allocations"
            ]
        )

        if not allocations:
            raise (
                forms.ValidationError(
                    "At least one "
                    "allocation is "
                    "required."
                )
            )

        return allocations


class PaymentVoidForm(
    forms.Form
):
    reason = forms.CharField(
        strip=True,
    )