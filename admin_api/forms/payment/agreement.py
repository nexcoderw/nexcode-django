from decimal import Decimal

from django import forms

from home.models import (
    PaymentAgreement,
    Portfolio,
)


AGREEMENT_FIELDS = (
    "portfolio_id",
    "title",
    "reference",
    "agreement_type",
    "currency",
    "total_amount",
    "agreement_date",
    "start_date",
    "end_date",
    "status",
    "notes",
)


class PaymentAgreementCreateForm(
    forms.Form
):
    portfolio_id = (
        forms.ModelChoiceField(
            queryset=(
                Portfolio.objects.all()
            ),
        )
    )

    title = forms.CharField(
        max_length=255,
        strip=True,
    )

    reference = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
    )

    agreement_type = (
        forms.ChoiceField(
            choices=(
                PaymentAgreement
                .AgreementType
                .choices
            ),
        )
    )

    currency = forms.ChoiceField(
        choices=(
            PaymentAgreement
            .Currency
            .choices
        ),
    )

    total_amount = (
        forms.DecimalField(
            max_digits=18,
            decimal_places=2,
            min_value=Decimal(
                "0.01"
            ),
        )
    )

    agreement_date = (
        forms.DateField()
    )

    start_date = (
        forms.DateField()
    )

    end_date = forms.DateField(
        required=False,
    )

    status = forms.ChoiceField(
        choices=(
            PaymentAgreement
            .Status
            .choices
        ),
        required=False,
    )

    notes = forms.CharField(
        required=False,
        strip=True,
    )

    def clean(self):
        data = super().clean()

        _validate_dates(
            data
        )

        return data


class PaymentAgreementUpdateForm(
    forms.Form
):
    portfolio_id = (
        forms.ModelChoiceField(
            queryset=(
                Portfolio.objects.all()
            ),
            required=False,
        )
    )

    title = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    reference = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
    )

    agreement_type = (
        forms.ChoiceField(
            choices=(
                PaymentAgreement
                .AgreementType
                .choices
            ),
            required=False,
        )
    )

    currency = forms.ChoiceField(
        choices=(
            PaymentAgreement
            .Currency
            .choices
        ),
        required=False,
    )

    total_amount = (
        forms.DecimalField(
            max_digits=18,
            decimal_places=2,
            min_value=Decimal(
                "0.01"
            ),
            required=False,
        )
    )

    agreement_date = (
        forms.DateField(
            required=False,
        )
    )

    start_date = forms.DateField(
        required=False,
    )

    end_date = forms.DateField(
        required=False,
    )

    status = forms.ChoiceField(
        choices=(
            PaymentAgreement
            .Status
            .choices
        ),
        required=False,
    )

    notes = forms.CharField(
        required=False,
        strip=True,
    )

    def __init__(
        self,
        *args,
        agreement=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.agreement = agreement

    def clean(self):
        data = super().clean()

        if not (
            set(self.data.keys())
            & set(
                AGREEMENT_FIELDS
            )
        ):
            raise (
                forms.ValidationError(
                    "No agreement changes "
                    "were provided."
                )
            )

        for field in (
            "portfolio_id",
            "title",
            "agreement_type",
            "currency",
            "total_amount",
            "agreement_date",
            "start_date",
            "status",
        ):
            if (
                field in self.data
                and not data.get(
                    field
                )
            ):
                self.add_error(
                    field,
                    (
                        f"{field} cannot "
                        "be empty."
                    ),
                )

        if self.agreement:
            start_date = (
                data.get(
                    "start_date"
                )
                if (
                    "start_date"
                    in self.data
                )
                else (
                    self.agreement
                    .start_date
                )
            )

            end_date = (
                data.get(
                    "end_date"
                )
                if (
                    "end_date"
                    in self.data
                )
                else (
                    self.agreement
                    .end_date
                )
            )

            agreement_type = (
                data.get(
                    "agreement_type"
                )
                if (
                    "agreement_type"
                    in self.data
                )
                else (
                    self.agreement
                    .agreement_type
                )
            )

            _validate_dates(
                {
                    "start_date":
                        start_date,
                    "end_date":
                        end_date,
                    "agreement_type":
                        agreement_type,
                },
                form=self,
            )

        return data


def _validate_dates(
    data,
    *,
    form=None,
):
    start_date = data.get(
        "start_date"
    )

    end_date = data.get(
        "end_date"
    )

    agreement_type = (
        data.get(
            "agreement_type"
        )
    )

    if (
        start_date
        and end_date
        and end_date
        < start_date
    ):
        if form:
            form.add_error(
                "end_date",
                (
                    "End date cannot "
                    "be before the "
                    "start date."
                ),
            )
        else:
            raise (
                forms.ValidationError(
                    {
                        "end_date": (
                            "End date cannot "
                            "be before the "
                            "start date."
                        )
                    }
                )
            )

    if (
        agreement_type
        == (
            PaymentAgreement
            .AgreementType
            .MAINTENANCE
        )
        and not end_date
    ):
        if form:
            form.add_error(
                "end_date",
                (
                    "Maintenance "
                    "agreements require "
                    "an end date."
                ),
            )
        else:
            raise (
                forms.ValidationError(
                    {
                        "end_date": (
                            "Maintenance "
                            "agreements "
                            "require an "
                            "end date."
                        )
                    }
                )
            )