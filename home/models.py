from uuid import uuid4
from django.core.exceptions import (
    ValidationError,
)
from django.db import models
from django.db.models import (
    F,
    Q,
)
from django.utils import timezone
from django.utils.text import slugify
from home.upload_paths import (
    portfolio_document_path,
    portfolio_gallery_image_path,
    team_image_path,
    team_png_image_path,
)
from home.storages import (
    raw_media_storage,
)

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


# Historical migrations still import these paths from home.models.
def _legacy_image_path(folder, label):
    name = slugify(label or "") or "item"
    return f"{folder}/{name}/{uuid4().hex}.jpg"


def logo_image_path(instance, filename):
    return f"settings/branding/{uuid4().hex}.png"


def client_image_path(instance, filename):
    return _legacy_image_path("clients/profiles", instance.name)


def portfolio_image_path(instance, filename):
    name = getattr(instance, "name", None)
    if not name:
        name = getattr(getattr(instance, "portfolio", None), "name", None)
    return _legacy_image_path("portfolios/images", name)


def blog_image_path(instance, filename):
    return _legacy_image_path("blogs/featured", instance.title)


def training_image_path(instance, filename):
    return _legacy_image_path("trainings/images", instance.title)

class Team(models.Model):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    position = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    image = ProcessedImageField(
        upload_to=team_image_path,
        processors=[
            ResizeToFill(
                1333,
                1694,
            ),
        ],
        format="JPEG",
        options={
            "quality": 90,
        },
        null=True,
        blank=True,
    )

    image_png = models.ImageField(
        upload_to=team_png_image_path,
        null=True,
        blank=True,
    )

    linkedin = models.URLField(
        null=True,
        blank=True,
    )

    github = models.URLField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def _generate_unique_slug(self):
        base_slug = (
            slugify(
                self.name or ""
            )
            or "team-member"
        )

        slug = base_slug

        while Team.objects.filter(
            slug=slug,
        ).exclude(
            pk=self.pk,
        ).exists():
            slug = (
                f"{base_slug}-"
                f"{uuid4().hex[:8]}"
            )

        return slug

    def save(
        self,
        *args,
        **kwargs,
    ):
        name_changed = True

        if self.pk:
            original = (
                Team.objects.filter(
                    pk=self.pk,
                )
                .only(
                    "name",
                    "slug",
                )
                .first()
            )

            if original is not None:
                name_changed = (
                    original.name
                    != self.name
                )

        if (
            not self.slug
            or name_changed
        ):
            self.slug = (
                self._generate_unique_slug()
            )

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return (
            self.name
            or "Unnamed Team Member"
        )

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = (
            "Team Members"
        )

class Portfolio(models.Model):
    class Category(
        models.TextChoices
    ):
        WEB_APPLICATION = (
            "web_application",
            "Web Application",
        )

        MOBILE_APPLICATION = (
            "mobile_application",
            "Mobile Application",
        )

        UI_UX = (
            "ui_ux",
            "UI/UX",
        )

        BRANDING = (
            "branding",
            "Branding",
        )

    class ProjectType(
        models.TextChoices
    ):
        CLIENT_PROJECT = (
            "client_project",
            "Client Project",
        )

        STUDENT_PROJECT = (
            "student_project",
            "Student Project",
        )

        LEARNING_PROJECT = (
            "learning_project",
            "Learning Project",
        )

    class Status(
        models.TextChoices
    ):
        DRAFT = (
            "draft",
            "Draft",
        )

        PUBLISHED = (
            "published",
            "Published",
        )

        ARCHIVED = (
            "archived",
            "Archived",
        )

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    summary = models.CharField(
        max_length=300,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
    )

    project_type = models.CharField(
        max_length=50,
        choices=ProjectType.choices,
    )

    live_url = models.URLField(
        max_length=500,
        blank=True,
    )

    figma_url = models.URLField(
        max_length=500,
        blank=True,
    )

    team_members = (
        models.ManyToManyField(
            Team,
            related_name="portfolios",
            blank=True,
        )
    )

    project_initiation_date = (
        models.DateField(
            null=True,
            blank=True,
        )
    )

    deadline_date = (
        models.DateField(
            null=True,
            blank=True,
        )
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    published_at = (
        models.DateTimeField(
            null=True,
            blank=True,
        )
    )

    created_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    updated_at = (
        models.DateTimeField(
            auto_now=True,
        )
    )

    def _generate_unique_slug(
        self,
    ):
        base_slug = (
            slugify(
                self.name or ""
            )
            or "portfolio"
        )

        slug = base_slug

        while (
            Portfolio.objects
            .filter(
                slug=slug,
            )
            .exclude(
                pk=self.pk,
            )
            .exists()
        ):
            slug = (
                f"{base_slug}-"
                f"{uuid4().hex[:8]}"
            )

        return slug

    def clean(self):
        super().clean()

        if (
            self.project_initiation_date
            and self.deadline_date
            and self.deadline_date
            < self.project_initiation_date
        ):
            raise ValidationError(
                {
                    "deadline_date": (
                        "Deadline cannot be "
                        "before the project "
                        "initiation date."
                    ),
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        if not self.slug:
            self.slug = (
                self._generate_unique_slug()
            )

        if (
            self.status
            == self.Status.PUBLISHED
            and self.published_at
            is None
        ):
            self.published_at = (
                timezone.now()
            )

        if (
            self.status
            == self.Status.DRAFT
        ):
            self.published_at = None

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return self.name

    class Meta:
        ordering = (
            "-created_at",
            "-pk",
        )

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        project_initiation_date__isnull=True
                    )
                    | Q(
                        deadline_date__isnull=True
                    )
                    | Q(
                        deadline_date__gte=F(
                            "project_initiation_date"
                        )
                    )
                ),
                name=(
                    "portfolio_deadline_"
                    "on_or_after_start"
                ),
            ),
        ]


class PortfolioImage(
    models.Model
):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = ProcessedImageField(
        upload_to=(
            portfolio_gallery_image_path
        ),
        processors=[
            ResizeToFill(
                1920,
                1350,
            ),
        ],
        format="JPEG",
        options={
            "quality": 90,
        },
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
    )

    is_cover = models.BooleanField(
        default=False,
    )

    position = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    created_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    updated_at = (
        models.DateTimeField(
            auto_now=True,
        )
    )

    def __str__(self):
        return (
            f"Image for "
            f"{self.portfolio.name}"
        )

    class Meta:
        ordering = (
            "position",
            "pk",
        )

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "portfolio",
                ),
                condition=Q(
                    is_cover=True,
                ),
                name=(
                    "unique_portfolio_"
                    "cover_image"
                ),
            ),
        ]


class PortfolioDocument(
    models.Model
):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(
        max_length=255,
    )

    url = models.URLField(
        max_length=1000,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.title} — "
            f"{self.portfolio.name}"
        )

    class Meta:
        ordering = (
            "pk",
        )

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "portfolio",
                    "url",
                ),
                name=(
                    "unique_portfolio_"
                    "document_url"
                ),
            ),
        ]


class PortfolioRepository(
    models.Model
):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="repositories",
    )

    label = models.CharField(
        max_length=100,
        default="Repository",
    )

    url = models.URLField(
        max_length=500,
    )

    created_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    updated_at = (
        models.DateTimeField(
            auto_now=True,
        )
    )

    def __str__(self):
        return (
            f"{self.label} — "
            f"{self.portfolio.name}"
        )

    class Meta:
        ordering = (
            "pk",
        )

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "portfolio",
                    "url",
                ),
                name=(
                    "unique_portfolio_"
                    "repository_url"
                ),
            ),
        ]