from urllib.parse import urlparse

from django import forms


MAX_TEAM_IMAGE_BYTES = (
    10 * 1024 * 1024
)

ALLOWED_TEAM_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


class TeamCreateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        strip=True,
    )

    position = forms.CharField(
        max_length=255,
        strip=True,
    )

    image = forms.ImageField(
        required=False,
    )

    image_png = forms.ImageField(
        required=False,
    )

    linkedin = forms.URLField(
        required=False,
    )

    github = forms.URLField(
        required=False,
    )

    # Optional: a new member without one is placed after everyone else.
    display_order = forms.IntegerField(
        required=False,
        min_value=0,
    )

    def clean_image(self):
        return _validate_image(
            self.cleaned_data.get(
                "image"
            )
        )

    def clean_image_png(self):
        image = _validate_image(
            self.cleaned_data.get(
                "image_png"
            )
        )

        if image:
            image_format = getattr(
                image.image,
                "format",
                None,
            )

            if image_format != "PNG":
                raise forms.ValidationError(
                    "The cutout image "
                    "must be a PNG file."
                )

        return image

    def clean_linkedin(self):
        return _validate_domain(
            self.cleaned_data.get(
                "linkedin"
            ),
            "linkedin.com",
            "LinkedIn",
        )

    def clean_github(self):
        return _validate_domain(
            self.cleaned_data.get(
                "github"
            ),
            "github.com",
            "GitHub",
        )


class TeamUpdateForm(
    TeamCreateForm
):
    name = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    position = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    remove_image = (
        forms.BooleanField(
            required=False,
        )
    )

    remove_image_png = (
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
            "position" in self.data
            and not cleaned_data.get(
                "position"
            )
        ):
            self.add_error(
                "position",
                (
                    "Position cannot "
                    "be empty."
                ),
            )

        if (
            cleaned_data.get(
                "remove_image"
            )
            and cleaned_data.get(
                "image"
            )
        ):
            self.add_error(
                "image",
                (
                    "Upload a replacement "
                    "or remove the image, "
                    "not both."
                ),
            )

        if (
            cleaned_data.get(
                "remove_image_png"
            )
            and cleaned_data.get(
                "image_png"
            )
        ):
            self.add_error(
                "image_png",
                (
                    "Upload a replacement "
                    "or remove the PNG, "
                    "not both."
                ),
            )

        editable_fields = {
            "name",
            "position",
            "image",
            "image_png",
            "linkedin",
            "github",
            "display_order",
            "remove_image",
            "remove_image_png",
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
                "No team member changes "
                "were provided."
            )

        return cleaned_data


def _validate_image(image):
    if not image:
        return image

    if (
        image.size
        > MAX_TEAM_IMAGE_BYTES
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
        not in ALLOWED_TEAM_IMAGE_FORMATS
    ):
        raise forms.ValidationError(
            "Supported image formats are "
            "JPEG, PNG, and WebP."
        )

    return image


def _validate_domain(
    value,
    expected_domain,
    label,
):
    if not value:
        return value

    hostname = (
        urlparse(value)
        .hostname
        or ""
    ).lower()

    valid = (
        hostname
        == expected_domain
        or hostname.endswith(
            f".{expected_domain}"
        )
    )

    if not valid:
        raise forms.ValidationError(
            f"Enter a valid {label} URL."
        )

    return value