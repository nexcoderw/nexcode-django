from decimal import Decimal
from uuid import uuid4

from django.conf import settings
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
from home.image_processing import (
    WEB_IMAGE_FORMAT,
    portfolio_image_processors,
    portrait_processors,
    transparent_cutout_options,
    transparent_cutout_processors,
    web_image_options,
)
from home.storages import (
    raw_media_storage,
)
from home.upload_paths import (
    portfolio_document_path,
    portfolio_gallery_image_path,
    team_image_path,
    team_png_image_path,
)

from imagekit.models import ProcessedImageField


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
        processors=portrait_processors(),
        format=WEB_IMAGE_FORMAT,
        options=web_image_options(),
        null=True,
        blank=True,
    )

    image_png = ProcessedImageField(
        upload_to=team_png_image_path,
        processors=(
            transparent_cutout_processors()
        ),
        format=WEB_IMAGE_FORMAT,
        options=transparent_cutout_options(),
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

    # Where the member appears on the public site and in the admin:
    # lower numbers first, ties broken by name.
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
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
        ordering = (
            "display_order",
            "name",
            "pk",
        )
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

    @property
    def cover_image(self):
        # Reads images.all() so a prefetch_related("images") is reused
        # instead of querying once per portfolio in a list.
        images = list(self.images.all())

        return next(
            (image for image in images if image.is_cover),
            images[0] if images else None,
        )

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
        processors=(
            portfolio_image_processors()
        ),
        format=WEB_IMAGE_FORMAT,
        options=web_image_options(),
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

class Client(
    models.Model
):
    """A client the admin keeps contact details for.

    Only identity and contact information is stored. The client is
    managed from the admin portal and never shown on the public site.
    """

    name = models.CharField(
        max_length=255,
    )

    email = models.EmailField(
        blank=True,
    )

    phone_number = models.CharField(
        max_length=50,
        blank=True,
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
        return self.name

    class Meta:
        ordering = (
            "-created_at",
            "-pk",
        )

class Contact(
    models.Model
):
    """A message submitted through the public contact form."""

    class DeviceType(
        models.TextChoices
    ):
        DESKTOP = (
            "desktop",
            "Desktop",
        )

        MOBILE = (
            "mobile",
            "Mobile",
        )

        TABLET = (
            "tablet",
            "Tablet",
        )

        BOT = (
            "bot",
            "Bot",
        )

        UNKNOWN = (
            "unknown",
            "Unknown",
        )

    name = models.CharField(
        max_length=255,
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    # Who sent the message, recorded at submission so the admin can
    # recognise repeat senders and spam. Null when the address could not
    # be determined.
    ip_address = (
        models.GenericIPAddressField(
            null=True,
            blank=True,
        )
    )

    user_agent = models.CharField(
        max_length=512,
        blank=True,
    )

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.UNKNOWN,
    )

    browser = models.CharField(
        max_length=64,
        blank=True,
    )

    operating_system = models.CharField(
        max_length=64,
        blank=True,
    )

    # Set when an administrator first answers the message.
    replied_at = (
        models.DateTimeField(
            null=True,
            blank=True,
            db_index=True,
        )
    )

    created_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    def __str__(self):
        return (
            f"{self.subject} — "
            f"{self.name}"
        )

    class Meta:
        ordering = (
            "-created_at",
            "-pk",
        )

        verbose_name = "Contact"
        verbose_name_plural = (
            "Contacts"
        )


class ContactReply(
    models.Model
):
    """An email an administrator sent in answer to a contact message."""

    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    subject = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    # Kept when the administrator's account is removed, so the history
    # still shows that a reply went out.
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_replies",
    )

    sent_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    def __str__(self):
        return self.subject

    class Meta:
        ordering = (
            "-sent_at",
            "-pk",
        )

        verbose_name = "Contact reply"
        verbose_name_plural = (
            "Contact replies"
        )

class PaymentAgreement(
    models.Model
):
    class AgreementType(
        models.TextChoices
    ):
        PROJECT = (
            "project",
            "Project",
        )

        MAINTENANCE = (
            "maintenance",
            "Maintenance",
        )

        CUSTOM = (
            "custom",
            "Custom",
        )

    class Status(
        models.TextChoices
    ):
        DRAFT = (
            "draft",
            "Draft",
        )

        ACTIVE = (
            "active",
            "Active",
        )

        COMPLETED = (
            "completed",
            "Completed",
        )

        CANCELLED = (
            "cancelled",
            "Cancelled",
        )

    class Currency(
        models.TextChoices
    ):
        RWF = (
            "RWF",
            "Rwandan Franc",
        )

        USD = (
            "USD",
            "US Dollar",
        )

        EUR = (
            "EUR",
            "Euro",
        )

        GBP = (
            "GBP",
            "British Pound",
        )

    portfolio = (
        models.ForeignKey(
            Portfolio,
            on_delete=models.PROTECT,
            related_name=(
                "payment_agreements"
            ),
        )
    )

    title = models.CharField(
        max_length=255,
    )

    reference = (
        models.CharField(
            max_length=100,
            blank=True,
        )
    )

    agreement_type = (
        models.CharField(
            max_length=20,
            choices=(
                AgreementType
                .choices
            ),
            default=(
                AgreementType
                .PROJECT
            ),
            db_index=True,
        )
    )

    currency = (
        models.CharField(
            max_length=3,
            choices=Currency.choices,
            default=Currency.RWF,
        )
    )

    total_amount = (
        models.DecimalField(
            max_digits=18,
            decimal_places=2,
        )
    )

    agreement_date = (
        models.DateField()
    )

    start_date = (
        models.DateField()
    )

    end_date = (
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

    notes = models.TextField(
        blank=True,
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

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.end_date
            and self.end_date
            < self.start_date
        ):
            errors[
                "end_date"
            ] = (
                "Agreement end date "
                "cannot be before its "
                "start date."
            )

        if (
            self.agreement_type
            == self.AgreementType
            .MAINTENANCE
            and not self.end_date
        ):
            errors[
                "end_date"
            ] = (
                "Maintenance "
                "agreements require "
                "an end date."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def __str__(self):
        return (
            f"{self.title} — "
            f"{self.portfolio.name}"
        )

    class Meta:
        ordering = (
            "-created_at",
            "-pk",
        )

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    total_amount__gt=0,
                ),
                name=(
                    "payment_agreement_"
                    "positive_total"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        end_date__isnull=True,
                    )
                    | Q(
                        end_date__gte=F(
                            "start_date"
                        ),
                    )
                ),
                name=(
                    "payment_agreement_"
                    "end_after_start"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    ~Q(
                        agreement_type=(
                            "maintenance"
                        ),
                    )
                    | Q(
                        end_date__isnull=False,
                    )
                ),
                name=(
                    "payment_agreement_"
                    "maintenance_has_end"
                ),
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=(
                        "draft",
                        "active",
                        "completed",
                        "cancelled",
                    ),
                ),
                name=(
                    "payment_agreement_"
                    "valid_status"
                ),
            ),
            models.CheckConstraint(
                condition=Q(
                    agreement_type__in=(
                        "project",
                        "maintenance",
                        "custom",
                    ),
                ),
                name=(
                    "payment_agreement_"
                    "valid_type"
                ),
            ),
            models.CheckConstraint(
                condition=Q(
                    currency__in=(
                        "RWF",
                        "USD",
                        "EUR",
                        "GBP",
                    ),
                ),
                name=(
                    "payment_agreement_"
                    "valid_currency"
                ),
            ),
        ]


class PaymentInstallment(
    models.Model
):
    class Type(
        models.TextChoices
    ):
        DOWN_PAYMENT = (
            "down_payment",
            "Down Payment",
        )

        INSTALLMENT = (
            "installment",
            "Installment",
        )

        FINAL_PAYMENT = (
            "final_payment",
            "Final Payment",
        )

        MILESTONE = (
            "milestone",
            "Milestone",
        )

        MAINTENANCE = (
            "maintenance",
            "Maintenance",
        )

        CUSTOM = (
            "custom",
            "Custom",
        )

    class DueType(
        models.TextChoices
    ):
        FIXED_DATE = (
            "fixed_date",
            "Fixed Date",
        )

        MILESTONE = (
            "milestone",
            "Milestone",
        )

    agreement = (
        models.ForeignKey(
            PaymentAgreement,
            on_delete=models.CASCADE,
            related_name=(
                "installments"
            ),
        )
    )

    sequence = (
        models.PositiveIntegerField()
    )

    title = models.CharField(
        max_length=255,
    )

    installment_type = (
        models.CharField(
            max_length=30,
            choices=Type.choices,
            default=Type.INSTALLMENT,
            db_index=True,
        )
    )

    amount = (
        models.DecimalField(
            max_digits=18,
            decimal_places=2,
        )
    )

    due_type = (
        models.CharField(
            max_length=20,
            choices=DueType.choices,
            default=(
                DueType.FIXED_DATE
            ),
        )
    )

    # Forecast date. This always exists,
    # including milestone payments where
    # the exact date is not yet known.
    expected_due_date = (
        models.DateField(
            db_index=True,
        )
    )

    # Confirmed contractual/operational
    # date. Fixed-date payments require it.
    # Milestones may receive it later.
    due_date = (
        models.DateField(
            null=True,
            blank=True,
            db_index=True,
        )
    )

    milestone = (
        models.CharField(
            max_length=255,
            blank=True,
        )
    )

    grace_period_days = (
        models.PositiveSmallIntegerField(
            default=0,
        )
    )

    is_waived = (
        models.BooleanField(
            default=False,
            db_index=True,
        )
    )

    waived_at = (
        models.DateTimeField(
            null=True,
            blank=True,
        )
    )

    waiver_reason = (
        models.TextField(
            blank=True,
        )
    )

    notes = models.TextField(
        blank=True,
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

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.due_type
            == self.DueType
            .FIXED_DATE
            and not self.due_date
        ):
            errors[
                "due_date"
            ] = (
                "Fixed-date payments "
                "require a due date."
            )

        if (
            self.due_type
            == self.DueType
            .MILESTONE
            and not self.milestone
            .strip()
        ):
            errors[
                "milestone"
            ] = (
                "Milestone payments "
                "require a milestone."
            )

        if self.is_waived:
            if not self.waived_at:
                errors[
                    "waived_at"
                ] = (
                    "Waived payments "
                    "require the time "
                    "they were waived."
                )

            if (
                not self
                .waiver_reason
                .strip()
            ):
                errors[
                    "waiver_reason"
                ] = (
                    "Waived payments "
                    "require a reason."
                )

        else:
            if self.waived_at:
                errors[
                    "waived_at"
                ] = (
                    "A non-waived "
                    "payment cannot "
                    "have a waiver "
                    "timestamp."
                )

            if (
                self
                .waiver_reason
                .strip()
            ):
                errors[
                    "waiver_reason"
                ] = (
                    "A non-waived "
                    "payment cannot "
                    "have a waiver "
                    "reason."
                )

        if errors:
            raise ValidationError(
                errors
            )

    def __str__(self):
        return (
            f"{self.title} — "
            f"{self.agreement.title}"
        )

    class Meta:
        ordering = (
            "agreement_id",
            "sequence",
            "pk",
        )

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    sequence__gt=0,
                ),
                name=(
                    "payment_installment_"
                    "positive_sequence"
                ),
            ),
            models.CheckConstraint(
                condition=Q(
                    amount__gt=0,
                ),
                name=(
                    "payment_installment_"
                    "positive_amount"
                ),
            ),
            models.UniqueConstraint(
                fields=(
                    "agreement",
                    "sequence",
                ),
                name=(
                    "unique_payment_"
                    "installment_sequence"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        due_type=(
                            "fixed_date"
                        ),
                        due_date__isnull=False,
                        milestone="",
                    )
                    | (
                        Q(
                            due_type=(
                                "milestone"
                            ),
                        )
                        & ~Q(
                            milestone="",
                        )
                    )
                ),
                name=(
                    "payment_installment_"
                    "valid_due_rule"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        is_waived=False,
                        waived_at__isnull=True,
                        waiver_reason="",
                    )
                    | (
                        Q(
                            is_waived=True,
                            waived_at__isnull=False,
                        )
                        & ~Q(
                            waiver_reason="",
                        )
                    )
                ),
                name=(
                    "payment_installment_"
                    "valid_waiver"
                ),
            ),
        ]


class PaymentRecord(
    models.Model
):
    class Method(
        models.TextChoices
    ):
        BANK_TRANSFER = (
            "bank_transfer",
            "Bank Transfer",
        )

        MOBILE_MONEY = (
            "mobile_money",
            "Mobile Money",
        )

        CASH = (
            "cash",
            "Cash",
        )

        CARD = (
            "card",
            "Card",
        )

        CHEQUE = (
            "cheque",
            "Cheque",
        )

        OTHER = (
            "other",
            "Other",
        )

    class Status(
        models.TextChoices
    ):
        POSTED = (
            "posted",
            "Posted",
        )

        VOIDED = (
            "voided",
            "Voided",
        )

    agreement = (
        models.ForeignKey(
            PaymentAgreement,
            on_delete=models.PROTECT,
            related_name="payments",
        )
    )

    amount = (
        models.DecimalField(
            max_digits=18,
            decimal_places=2,
        )
    )

    currency = (
        models.CharField(
            max_length=3,
            choices=(
                PaymentAgreement
                .Currency
                .choices
            ),
            default=(
                PaymentAgreement
                .Currency
                .RWF
            ),
        )
    )

    paid_at = (
        models.DateTimeField(
            default=timezone.now,
            db_index=True,
        )
    )

    payment_method = (
        models.CharField(
            max_length=30,
            choices=Method.choices,
            default=(
                Method.BANK_TRANSFER
            ),
        )
    )

    reference = (
        models.CharField(
            max_length=255,
            blank=True,
        )
    )

    notes = models.TextField(
        blank=True,
    )

    recorded_by = (
        models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            related_name=(
                "recorded_payments"
            ),
            null=True,
            blank=True,
        )
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.POSTED,
        db_index=True,
    )

    voided_at = (
        models.DateTimeField(
            null=True,
            blank=True,
        )
    )

    void_reason = (
        models.TextField(
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

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.agreement_id
            and self.currency
            != self.agreement.currency
        ):
            errors[
                "currency"
            ] = (
                "Payment currency "
                "must match the "
                "agreement currency."
            )

        if (
            self.status
            == self.Status.VOIDED
        ):
            if not self.voided_at:
                errors[
                    "voided_at"
                ] = (
                    "Voided payments "
                    "require the time "
                    "they were voided."
                )

            if (
                not self
                .void_reason
                .strip()
            ):
                errors[
                    "void_reason"
                ] = (
                    "Voided payments "
                    "require a reason."
                )

        else:
            if self.voided_at:
                errors[
                    "voided_at"
                ] = (
                    "Posted payments "
                    "cannot have a "
                    "void timestamp."
                )

            if (
                self
                .void_reason
                .strip()
            ):
                errors[
                    "void_reason"
                ] = (
                    "Posted payments "
                    "cannot have a "
                    "void reason."
                )

        if errors:
            raise ValidationError(
                errors
            )

    def __str__(self):
        return (
            f"{self.amount} "
            f"{self.currency} — "
            f"{self.agreement.title}"
        )

    class Meta:
        ordering = (
            "-paid_at",
            "-pk",
        )

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    amount__gt=0,
                ),
                name=(
                    "payment_record_"
                    "positive_amount"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        status="posted",
                        voided_at__isnull=True,
                        void_reason="",
                    )
                    | (
                        Q(
                            status="voided",
                            voided_at__isnull=False,
                        )
                        & ~Q(
                            void_reason="",
                        )
                    )
                ),
                name=(
                    "payment_record_"
                    "valid_void_state"
                ),
            ),
            models.CheckConstraint(
                condition=Q(
                    currency__in=(
                        "RWF",
                        "USD",
                        "EUR",
                        "GBP",
                    ),
                ),
                name=(
                    "payment_record_"
                    "valid_currency"
                ),
            ),
        ]


class PaymentAllocation(
    models.Model
):
    payment = models.ForeignKey(
        PaymentRecord,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    installment = (
        models.ForeignKey(
            PaymentInstallment,
            on_delete=models.PROTECT,
            related_name=(
                "allocations"
            ),
        )
    )

    amount = (
        models.DecimalField(
            max_digits=18,
            decimal_places=2,
        )
    )

    created_at = (
        models.DateTimeField(
            auto_now_add=True,
        )
    )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.payment_id
            and self.installment_id
            and (
                self.payment
                .agreement_id
                != self.installment
                .agreement_id
            )
        ):
            errors[
                "installment"
            ] = (
                "The payment and "
                "installment must "
                "belong to the same "
                "agreement."
            )

        if (
            self.payment_id
            and self.payment.status
            != PaymentRecord
            .Status.POSTED
        ):
            errors[
                "payment"
            ] = (
                "Voided payments "
                "cannot receive new "
                "allocations."
            )

        if (
            self.installment_id
            and self.installment
            .is_waived
        ):
            errors[
                "installment"
            ] = (
                "A waived installment "
                "cannot receive new "
                "allocations."
            )

        if (
            self.payment_id
            and self.amount
        ):
            allocated = (
                PaymentAllocation
                .objects
                .filter(
                    payment_id=(
                        self.payment_id
                    ),
                )
                .exclude(
                    pk=self.pk,
                )
                .aggregate(
                    total=models.Sum(
                        "amount"
                    ),
                )[
                    "total"
                ]
                or Decimal(
                    "0.00"
                )
            )

            if (
                allocated
                + self.amount
                > self.payment.amount
            ):
                errors[
                    "amount"
                ] = (
                    "Allocations cannot "
                    "exceed the payment "
                    "amount."
                )

        if (
            self.installment_id
            and self.amount
        ):
            allocated = (
                PaymentAllocation
                .objects
                .filter(
                    installment_id=(
                        self.installment_id
                    ),
                    payment__status=(
                        PaymentRecord
                        .Status
                        .POSTED
                    ),
                )
                .exclude(
                    pk=self.pk,
                )
                .aggregate(
                    total=models.Sum(
                        "amount"
                    ),
                )[
                    "total"
                ]
                or Decimal(
                    "0.00"
                )
            )

            if (
                allocated
                + self.amount
                > self.installment.amount
            ):
                errors[
                    "amount"
                ] = (
                    "Allocations cannot "
                    "exceed the "
                    "installment amount."
                )

        if errors:
            raise ValidationError(
                errors
            )

    def __str__(self):
        return (
            f"{self.amount} → "
            f"{self.installment.title}"
        )

    class Meta:
        ordering = (
            "created_at",
            "pk",
        )

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    amount__gt=0,
                ),
                name=(
                    "payment_allocation_"
                    "positive_amount"
                ),
            ),
            models.UniqueConstraint(
                fields=(
                    "payment",
                    "installment",
                ),
                name=(
                    "unique_payment_"
                    "allocation_pair"
                ),
            ),
        ]