from uuid import uuid4

from django.db import models
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Historical migrations still resolve these upload callables through home.models.
from home.upload_paths import (
    blog_image_path,
    client_image_path,
    logo_image_path,
    portfolio_image_path,
    team_image_path,
    team_png_image_path,
    training_image_path,
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
            slug=slug
        ).exclude(
            pk=self.pk
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
                    pk=self.pk
                )
                .only(
                    "name",
                    "slug",
                )
                .first()
            )

            name_changed = (
                original is None
                or self.name
                != original.name
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
        verbose_name_plural = (
            "Team Members"
        )


class Contact(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name and self.subject:
            return f"Message from {self.name} - {self.subject}"
        return "Unnamed Contact Message"

    class Meta:
        verbose_name_plural = "Contacts"


class Setting(models.Model):
    icon_black_logo = ProcessedImageField(
        upload_to=logo_image_path, format="PNG", options={"quality": 90}, null=True, blank=True
    )
    name_black_logo = ProcessedImageField(
        upload_to=logo_image_path, format="PNG", options={"quality": 90}, null=True, blank=True
    )
    icon_white_logo = ProcessedImageField(
        upload_to=logo_image_path, format="PNG", options={"quality": 90}, null=True, blank=True
    )
    name_white_logo = ProcessedImageField(
        upload_to=logo_image_path, format="PNG", options={"quality": 90}, null=True, blank=True
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    second_email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            raise ValueError("You can only create one instance of the settings.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Website Settings"

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
