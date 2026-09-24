"""The public contact form."""

from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "aria-label": "Name",
                "autocomplete": "name",
                "required": True,
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "aria-label": "Email",
                "autocomplete": "email",
                "required": True,
            }
        ),
    )

    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Subject",
                "aria-label": "Subject",
                "required": True,
            }
        ),
    )

    message = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Message",
                "aria-label": "Message",
                "rows": 4,
                "required": True,
            }
        ),
    )

    # A honeypot: hidden from people, so only bots fill it in.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
            }
        ),
    )

    def is_bot(self):
        return bool(self.cleaned_data.get("website"))
