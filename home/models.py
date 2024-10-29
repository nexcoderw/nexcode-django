import os
import random
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

def team_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'team/member_{slugify(instance.name)}_{instance.created_at}{file_extension}'

class Team(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    image = ProcessedImageField(
        upload_to=team_image_path,
        processors=[ResizeToFill(1333, 1694)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Team Members"

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.name} - {self.subject}'

def logo_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    random_number = random.randint(1000, 9999)
    return f'settings/logo/{random_number}_{instance.created_at}{file_extension}'

class Setting(models.Model):
    icon_black_logo = ProcessedImageField(
        upload_to=logo_image_path,
        # processors=[ResizeToFill(600, 600)],
        format='PNG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    name_black_logo = ProcessedImageField(
        upload_to=logo_image_path,
        # processors=[ResizeToFill(600, 600)],
        format='PNG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    icon_white_logo = ProcessedImageField(
        upload_to=logo_image_path,
        # processors=[ResizeToFill(600, 600)],
        format='PNG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    name_white_logo = ProcessedImageField(
        upload_to=logo_image_path,
        # processors=[ResizeToFill(600, 600)],
        format='PNG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    second_email = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure only one instance of settings can exist
        if not self.pk and Setting.objects.exists():
            raise ValueError("You can only create one instance of the settings.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Website Settings"

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"