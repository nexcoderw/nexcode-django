from django import forms


MAX_TEAM_IMAGE_BYTES = (
    10 * 1024 * 1024
)


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

    def clean_image(self):
        return _validate_image(
            self.cleaned_data.get(
                "image"
            ),
        )

    def clean_image_png(self):
        image = _validate_image(
            self.cleaned_data.get(
                "image_png"
            ),
        )

        if (
            image
            and getattr(
                image,
                "image",
                None,
            )
            and image.image.format
            != "PNG"
        ):
            raise forms.ValidationError(
                "The transparent image "
                "must be a PNG file."
            )

        return image


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

        supplied_fields = (
            set(self.data.keys())
            | set(self.files.keys())
        )

        editable_fields = {
            "name",
            "position",
            "image",
            "image_png",
            "linkedin",
            "github",
            "remove_image",
            "remove_image_png",
        }

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

    return image