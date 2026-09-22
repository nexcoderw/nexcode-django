import uuid

from django.conf import settings
from django.db import models


class AdminPasswordResetChallenge(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_password_reset_challenges",
    )

    code_hash = models.CharField(
        max_length=128,
    )

    reset_token_hash = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
    )

    expires_at = models.DateTimeField()

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reset_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    consumed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            "Admin password reset challenge "
            f"{self.pk}"
        )