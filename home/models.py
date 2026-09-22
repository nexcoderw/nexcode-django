from uuid import uuid4

from django.db import models
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from home.upload_paths import (
    team_image_path,
    team_png_image_path,
)


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