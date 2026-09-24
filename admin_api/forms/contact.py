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


class ContactReplyForm(
    forms.Form
):
    subject = forms.CharField(
        max_length=255,
        strip=True,
    )

    message = forms.CharField(
        max_length=10_000,
        strip=True,
    )

    def clean_subject(self):
        subject = self.cleaned_data[
            "subject"
        ]

        # A line break in an email header could smuggle in extra headers.
        if (
            "\n" in subject
            or "\r" in subject
        ):
            raise forms.ValidationError(
                "The subject must "
                "be a single line."
            )

        return subject
