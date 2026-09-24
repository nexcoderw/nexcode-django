from django import forms


CLIENT_FIELDS = (
    "name",
    "email",
    "phone_number",
)


class ClientCreateForm(
    forms.Form
):
    name = forms.CharField(
        max_length=255,
        strip=True,
    )

    email = forms.EmailField(
        required=False,
    )

    phone_number = forms.CharField(
        max_length=50,
        required=False,
        strip=True,
    )


class ClientUpdateForm(
    ClientCreateForm
):
    name = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        if not (
            set(self.data.keys())
            & set(CLIENT_FIELDS)
        ):
            raise forms.ValidationError(
                "No client changes "
                "were provided."
            )

        if (
            "name" in self.data
            and not cleaned_data.get(
                "name"
            )
        ):
            self.add_error(
                "name",
                "Name cannot be empty.",
            )

        return cleaned_data
