from django import forms

from home.models import Client


MAX_CLIENT_IMAGE_BYTES = (
    10 * 1024 * 1024
)

ALLOWED_CLIENT_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


class ClientCreateForm(
    forms.Form
):
    name = forms.CharField(
        max_length=255,
        strip=True,
    )

    company_name = (
        forms.CharField(
            max_length=255,
            required=False,
            strip=True,
        )
    )

    email = forms.EmailField(
        required=False,
    )

    phone = forms.CharField(
        max_length=50,
        required=False,
        strip=True,
    )

    website = forms.URLField(
        max_length=500,
        required=False,
    )

    location = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    profile_image = (
        forms.ImageField(
            required=False,
        )
    )

    notes = forms.CharField(
        required=False,
        strip=True,
    )

    status = forms.ChoiceField(
        choices=Client.Status.choices,
        required=False,
    )

    def clean_profile_image(
        self,
    ):
        return _validate_image(
            self.cleaned_data.get(
                "profile_image"
            )
        )


class ClientUpdateForm(
    ClientCreateForm
):
    name = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    remove_profile_image = (
        forms.BooleanField(
            required=False,
        )
    )

    def clean(self):
        cleaned_data = (
            super().clean()
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

        if (
            cleaned_data.get(
                "remove_profile_image"
            )
            and cleaned_data.get(
                "profile_image"
            )
        ):
            self.add_error(
                "profile_image",
                (
                    "Upload a replacement "
                    "or remove the profile "
                    "image, not both."
                ),
            )

        editable_fields = {
            "name",
            "company_name",
            "email",
            "phone",
            "website",
            "location",
            "profile_image",
            "notes",
            "status",
            "remove_profile_image",
        }

        supplied_fields = (
            set(self.data.keys())
            | set(self.files.keys())
        )

        if not (
            supplied_fields
            & editable_fields
        ):
            raise forms.ValidationError(
                "No client changes "
                "were provided."
            )

        return cleaned_data


def _validate_image(
    image,
):
    if not image:
        return image

    if (
        image.size
        > MAX_CLIENT_IMAGE_BYTES
    ):
        raise forms.ValidationError(
            "Image size cannot exceed "
            "10 MB."
        )

    image_format = getattr(
        image.image,
        "format",
        None,
    )

    if (
        image_format
        not in
        ALLOWED_CLIENT_IMAGE_FORMATS
    ):
        raise forms.ValidationError(
            "Supported image formats are "
            "JPEG, PNG, and WebP."
        )

    return image