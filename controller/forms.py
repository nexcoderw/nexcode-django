from django import forms
from home.models import *
from django.core.validators import RegexValidator

_phone_validator = RegexValidator(
    r"^\+?[0-9]{9,15}$",
    "Enter a valid phone number (9–15 digits, optional leading ‘+’)."
)

class ClientForm(forms.ModelForm):
    """Professional form for creating a Client with strong validation."""

    phone_number = forms.CharField(
        required=True,
        validators=[_phone_validator],
        widget=forms.TextInput(attrs={
            "placeholder": "Client Phone Number",
            "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                      "focus-visible:outline-none focus-visible:ring-2 "
                      "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
        })
    )

    class Meta:
        model  = Client
        fields = ("name", "email", "phone_number", "image")
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Client Name",
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Client Email",
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = Client.objects.filter(email__iexact=email)

        # ✨  Ignore the record we’re currently editing
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A client with this email already exists.")
        return email