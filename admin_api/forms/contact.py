from django import forms


class ContactCreateForm(
    forms.Form
):
    name = forms.CharField(
        max_length=255,
        strip=True,
    )

    email = forms.EmailField()

    subject = forms.CharField(
        max_length=255,
        strip=True,
    )

    message = forms.CharField(
        strip=True,
    )