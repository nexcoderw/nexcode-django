from django import forms

from home.models import (
    Portfolio,
    PortfolioDocument,
    PortfolioRepository,
    Team,
)


MAX_PORTFOLIO_IMAGE_BYTES = (
    10 * 1024 * 1024
)

ALLOWED_PORTFOLIO_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


class PortfolioCreateForm(
    forms.Form
):
    name = forms.CharField(
        max_length=255,
        strip=True,
    )

    summary = forms.CharField(
        max_length=300,
        required=False,
        strip=True,
    )

    description = forms.CharField(
        required=False,
        strip=True,
    )

    category = forms.ChoiceField(
        choices=(
            Portfolio.Category.choices
        ),
    )

    project_type = (
        forms.ChoiceField(
            choices=(
                Portfolio
                .ProjectType
                .choices
            ),
        )
    )

    live_url = forms.URLField(
        required=False,
    )

    figma_url = forms.URLField(
        required=False,
    )

    team_member_ids = (
        forms.ModelMultipleChoiceField(
            queryset=(
                Team.objects.all()
            ),
            required=False,
        )
    )

    project_initiation_date = (
        forms.DateField(
            required=False,
        )
    )

    deadline_date = (
        forms.DateField(
            required=False,
        )
    )

    status = forms.ChoiceField(
        choices=(
            Portfolio.Status.choices
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        start_date = (
            cleaned_data.get(
                "project_initiation_date"
            )
        )

        deadline_date = (
            cleaned_data.get(
                "deadline_date"
            )
        )

        if (
            start_date
            and deadline_date
            and deadline_date
            < start_date
        ):
            self.add_error(
                "deadline_date",
                (
                    "Deadline cannot be "
                    "before the project "
                    "initiation date."
                ),
            )

        return cleaned_data


class PortfolioUpdateForm(
    forms.Form
):
    name = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    summary = forms.CharField(
        max_length=300,
        required=False,
        strip=True,
    )

    description = forms.CharField(
        required=False,
        strip=True,
    )

    category = forms.ChoiceField(
        choices=(
            Portfolio.Category.choices
        ),
        required=False,
    )

    project_type = (
        forms.ChoiceField(
            choices=(
                Portfolio
                .ProjectType
                .choices
            ),
            required=False,
        )
    )

    live_url = forms.URLField(
        required=False,
    )

    figma_url = forms.URLField(
        required=False,
    )

    team_member_ids = (
        forms.ModelMultipleChoiceField(
            queryset=(
                Team.objects.all()
            ),
            required=False,
        )
    )

    project_initiation_date = (
        forms.DateField(
            required=False,
        )
    )

    deadline_date = (
        forms.DateField(
            required=False,
        )
    )

    status = forms.ChoiceField(
        choices=(
            Portfolio.Status.choices
        ),
        required=False,
    )

    def __init__(
        self,
        *args,
        portfolio=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.portfolio = (
            portfolio
        )

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        editable_fields = {
            "name",
            "summary",
            "description",
            "category",
            "project_type",
            "live_url",
            "figma_url",
            "team_member_ids",
            "project_initiation_date",
            "deadline_date",
            "status",
        }

        if not (
            set(self.data.keys())
            & editable_fields
        ):
            raise forms.ValidationError(
                (
                    "No portfolio changes "
                    "were provided."
                )
            )

        for field_name in (
            "name",
            "category",
            "project_type",
            "status",
        ):
            if (
                field_name
                in self.data
                and not cleaned_data.get(
                    field_name
                )
            ):
                self.add_error(
                    field_name,
                    (
                        f"{field_name}"
                        " cannot be empty."
                    ),
                )

        start_date = (
            cleaned_data.get(
                "project_initiation_date"
            )
            if (
                "project_initiation_date"
                in self.data
            )
            else getattr(
                self.portfolio,
                "project_initiation_date",
                None,
            )
        )

        deadline_date = (
            cleaned_data.get(
                "deadline_date"
            )
            if (
                "deadline_date"
                in self.data
            )
            else getattr(
                self.portfolio,
                "deadline_date",
                None,
            )
        )

        if (
            start_date
            and deadline_date
            and deadline_date
            < start_date
        ):
            self.add_error(
                "deadline_date",
                (
                    "Deadline cannot be "
                    "before the project "
                    "initiation date."
                ),
            )

        return cleaned_data


class PortfolioImageCreateForm(
    forms.Form
):
    image = forms.ImageField()

    alt_text = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    is_cover = forms.BooleanField(
        required=False,
    )

    position = forms.IntegerField(
        required=False,
        min_value=0,
    )

    def clean_image(self):
        return (
            _validate_portfolio_image(
                self.cleaned_data.get(
                    "image"
                )
            )
        )


class PortfolioImageUpdateForm(
    forms.Form
):
    image = forms.ImageField(
        required=False,
    )

    alt_text = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    is_cover = forms.BooleanField(
        required=False,
    )

    position = forms.IntegerField(
        required=False,
        min_value=0,
    )

    def clean_image(self):
        return (
            _validate_portfolio_image(
                self.cleaned_data.get(
                    "image"
                )
            )
        )

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        supplied = (
            set(self.data.keys())
            | set(self.files.keys())
        )

        if not (
            supplied
            & {
                "image",
                "alt_text",
                "is_cover",
                "position",
            }
        ):
            raise forms.ValidationError(
                (
                    "No image changes "
                    "were provided."
                )
            )

        return cleaned_data


class PortfolioDocumentCreateForm(
    forms.Form
):
    title = forms.CharField(
        max_length=255,
        strip=True,
    )

    url = forms.URLField(
        max_length=1000,
    )

    def __init__(
        self,
        *args,
        portfolio=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.portfolio = (
            portfolio
        )

    def clean_url(self):
        url = (
            self.cleaned_data["url"]
        )

        if (
            self.portfolio
            and PortfolioDocument
            .objects.filter(
                portfolio=(
                    self.portfolio
                ),
                url=url,
            )
            .exists()
        ):
            raise forms.ValidationError(
                (
                    "This document link "
                    "already exists."
                )
            )

        return url


class PortfolioDocumentUpdateForm(
    forms.Form
):
    title = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
    )

    url = forms.URLField(
        max_length=1000,
        required=False,
    )

    def __init__(
        self,
        *args,
        document=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.document = document

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        if not (
            set(self.data.keys())
            & {
                "title",
                "url",
            }
        ):
            raise forms.ValidationError(
                (
                    "No document changes "
                    "were provided."
                )
            )

        if (
            "title" in self.data
            and not cleaned_data.get(
                "title"
            )
        ):
            self.add_error(
                "title",
                (
                    "Document title "
                    "cannot be empty."
                ),
            )

        if (
            "url" in self.data
            and not cleaned_data.get(
                "url"
            )
        ):
            self.add_error(
                "url",
                (
                    "Document URL "
                    "cannot be empty."
                ),
            )

        url = cleaned_data.get(
            "url"
        )

        if (
            url
            and self.document
            and PortfolioDocument
            .objects.filter(
                portfolio=(
                    self.document
                    .portfolio
                ),
                url=url,
            )
            .exclude(
                pk=self.document.pk
            )
            .exists()
        ):
            self.add_error(
                "url",
                (
                    "This document link "
                    "already exists."
                ),
            )

        return cleaned_data


class PortfolioRepositoryCreateForm(
    forms.Form
):
    label = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
    )

    url = forms.URLField(
        max_length=500,
    )

    def __init__(
        self,
        *args,
        portfolio=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.portfolio = (
            portfolio
        )

    def clean_url(self):
        url = (
            self.cleaned_data["url"]
        )

        if (
            self.portfolio
            and PortfolioRepository
            .objects.filter(
                portfolio=(
                    self.portfolio
                ),
                url=url,
            )
            .exists()
        ):
            raise forms.ValidationError(
                (
                    "This repository "
                    "already exists."
                )
            )

        return url


class PortfolioRepositoryUpdateForm(
    forms.Form
):
    label = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
    )

    url = forms.URLField(
        max_length=500,
        required=False,
    )

    def __init__(
        self,
        *args,
        repository=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.repository = repository

    def clean(self):
        cleaned_data = (
            super().clean()
        )

        if not (
            set(self.data.keys())
            & {
                "label",
                "url",
            }
        ):
            raise forms.ValidationError(
                (
                    "No repository "
                    "changes were provided."
                )
            )

        if (
            "url" in self.data
            and not cleaned_data.get(
                "url"
            )
        ):
            self.add_error(
                "url",
                (
                    "Repository URL "
                    "cannot be empty."
                ),
            )

        url = cleaned_data.get(
            "url"
        )

        if (
            url
            and self.repository
            and PortfolioRepository
            .objects.filter(
                portfolio=(
                    self.repository
                    .portfolio
                ),
                url=url,
            )
            .exclude(
                pk=self.repository.pk
            )
            .exists()
        ):
            self.add_error(
                "url",
                (
                    "This repository "
                    "already exists."
                ),
            )

        return cleaned_data


def _validate_portfolio_image(
    image,
):
    if not image:
        return image

    if (
        image.size
        > MAX_PORTFOLIO_IMAGE_BYTES
    ):
        raise forms.ValidationError(
            (
                "Image size cannot "
                "exceed 10 MB."
            )
        )

    image_format = getattr(
        image.image,
        "format",
        None,
    )

    if (
        image_format
        not in
        ALLOWED_PORTFOLIO_IMAGE_FORMATS
    ):
        raise forms.ValidationError(
            (
                "Supported image formats "
                "are JPEG, PNG, and WebP."
            )
        )

    return image