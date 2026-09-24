from decimal import Decimal

from django import forms

from home.models import (
    PaymentInstallment,
)


INSTALLMENT_FIELDS = (
    "sequence",
    "title",
    "installment_type",
    "amount",
    "due_type",
    "expected_due_date",
    "due_date",
    "milestone",
    "grace_period_days",
    "notes",
)


class PaymentInstallmentCreateForm(
    forms.Form
):
    sequence = forms.IntegerField(
        min_value=1,
    )

    title = forms.CharField(
        max_length=255,
        strip=True,
    )

    installment_type = (
        forms.ChoiceField(
            choices=(
                PaymentInstallment
                .Type
                .choices
            ),
        )
    )

    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal(
            "0.01"
        ),
    )

    due_type = forms.ChoiceField(
        choices=(
            PaymentInstallment
            .DueType
            .choices
        ),
    )

    expected_due_date = (
        forms.DateField()
    )

    due_date = forms.DateField(
        required=False,
    )

    milestone = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    grace_period_days = (
        forms.IntegerField(
            min_value=0,
            required=False,
        )
    )

    notes = forms.CharField(
        required=False,
        strip=True,
    )

    def clean(self):
        data = super().clean()

        _validate_due_rule(
            data,
            self,
        )

        return data


class PaymentInstallmentUpdateForm(
    PaymentInstallmentCreateForm
):
    sequence = forms.IntegerField(
        min_value=1,
        required=False,
    )

    title = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    installment_type = (
        forms.ChoiceField(
            choices=(
                PaymentInstallment
                .Type
                .choices
            ),
            required=False,
        )
    )

    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal(
            "0.01"
        ),
        required=False,
    )

    due_type = forms.ChoiceField(
        choices=(
            PaymentInstallment
            .DueType
            .choices
        ),
        required=False,
    )

    expected_due_date = (
        forms.DateField(
            required=False,
        )
    )

    def __init__(
        self,
        *args,
        installment=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.installment = (
            installment
        )

    def clean(self):
        data = (
            forms.Form.clean(
                self
            )
        )

        if not (
            set(self.data.keys())
            & set(
                INSTALLMENT_FIELDS
            )
        ):
            raise (
                forms.ValidationError(
                    "No installment "
                    "changes were "
                    "provided."
                )
            )

        if not self.installment:
            return data

        merged = {}

        for field in (
            INSTALLMENT_FIELDS
        ):
            if field in self.data:
                merged[field] = (
                    data.get(field)
                )
            else:
                merged[field] = (
                    getattr(
                        self.installment,
                        field,
                    )
                )

        _validate_due_rule(
            merged,
            self,
        )

        return data


class MilestoneConfirmationForm(
    forms.Form
):
    due_date = forms.DateField()


class InstallmentWaiverForm(
    forms.Form
):
    reason = forms.CharField(
        strip=True,
    )


def _validate_due_rule(
    data,
    form,
):
    due_type = data.get(
        "due_type"
    )

    due_date = data.get(
        "due_date"
    )

    milestone = (
        data.get(
            "milestone",
            "",
        )
        or ""
    ).strip()

    if (
        due_type
        == (
            PaymentInstallment
            .DueType
            .FIXED_DATE
        )
        and not due_date
    ):
        form.add_error(
            "due_date",
            (
                "Fixed-date "
                "installments require "
                "a due date."
            ),
        )

    if (
        due_type
        == (
            PaymentInstallment
            .DueType
            .MILESTONE
        )
        and not milestone
    ):
        form.add_error(
            "milestone",
            (
                "Milestone payments "
                "require a milestone."
            ),
        )