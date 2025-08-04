import os
import random
import string
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.core.exceptions import ValidationError

class DeleteOldFileMixin:
    """
    Mixin to automatically delete old file(s) from storage when
    a FileField/ImageField is updated, and delete them when the model
    instance is deleted.
    """
    file_fields: list[str] = []

    def save(self, *args, **kwargs):
        # Fetch old instance (if any)
        try:
            old = self.__class__.objects.get(pk=self.pk)
        except self.__class__.DoesNotExist:
            old = None

        super().save(*args, **kwargs)

        # After saving, delete any old files that were replaced
        if old:
            for field in self.file_fields:
                old_file = getattr(old, field)
                new_file = getattr(self, field)
                if old_file and old_file != new_file:
                    old_file.delete(save=False)

    def delete(self, *args, **kwargs):
        # Before deleting instance, delete all files
        for field in self.file_fields:
            f = getattr(self, field)
            if f:
                f.delete(save=False)
        super().delete(*args, **kwargs)

def portfolio_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'portfolio/work_{slugify(instance.name)}_{timestamp}{file_extension}'

def team_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'team/member_{slugify(instance.name)}_{timestamp}{file_extension}'

def team_png_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'team/member_png_{slugify(instance.name)}_{timestamp}.png'

def logo_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)
    return f'settings/logo/{random_number}_{timestamp}{file_extension}'

def blog_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'blog/{slugify(instance.title)}_{timestamp}{file_extension}'

def client_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'clients/{slugify(instance.name)}_{timestamp}{file_extension}'

def training_image_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'trainings/training_{slugify(instance.title)}_{timestamp}.{ext}'

class Client(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=client_image_path,
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Client"
    
    class Meta:
        verbose_name_plural = "Clients"

class Portfolio(models.Model):
    CATEGORY_CHOICES = [
        ('Web App', 'Web App'),
        ('Logo', 'Logo'),
        ('UI/UX', 'UI/UX'),
        ('Mobile App', 'Mobile App'),
    ]
    PROJECT_CATEGORY_CHOICES = [
        ('Student Project', 'Student Project'),
        ('Client Project', 'Client Project'),
        ('Learning Project', 'Learning Project'),
    ]

    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=portfolio_image_path,
        processors=[ResizeToFill(1920, 1350)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    big_image = ProcessedImageField(
        upload_to=portfolio_image_path,
        processors=[ResizeToFill(2000, 1125)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=255, null=True, blank=True, choices=CATEGORY_CHOICES)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    repo_link = models.URLField(max_length=255, null=True, blank=True)
    figma_link = models.URLField(max_length=255, null=True, blank=True)
    project_category = models.CharField(max_length=255, choices=PROJECT_CATEGORY_CHOICES, null=True, blank=True)
    system_analysis_document = models.FileField(upload_to='portfolio/system_analysis/', null=True, blank=True)
    publish = models.BooleanField(default=False)
    
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='portfolios', null=True, blank=True)
    team_members = models.ManyToManyField('Team', related_name='portfolios', blank=True)
    contract_document = models.FileField(upload_to='portfolio/contracts/', null=True, blank=True)
    
    project_initiation_date = models.DateField(null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    
    project_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def total_amount_paid(self):
        """Calculate the total amount paid from associated payments."""
        total_paid = self.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
        return total_paid

    @property
    def payment_status(self):
        """Return the payment status: 'Partial' or 'Fully Paid'."""
        if self.total_amount_paid >= (self.project_amount or 0):
            return "Fully Paid"
        return "Partial"

    def _generate_random_number(self, length=7):
        """Generate a random number of specified length."""
        return ''.join(random.choices(string.digits, k=length))

    def _generate_unique_slug(self):
        """Generate a unique slug by appending 7 random numbers."""
        base_slug = slugify(self.name)
        random_number = self._generate_random_number()
        slug = f"{base_slug}-{random_number}"
        while Portfolio.objects.filter(slug=slug).exists():
            random_number = self._generate_random_number()
            slug = f"{base_slug}-{random_number}"
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super(Portfolio, self).save(*args, **kwargs)
        
        # Automatically create a Payment instance if project_amount is set and no payments exist
        if self.project_amount and not self.payments.exists():
            Payment.objects.create(portfolio=self, amount_paid=0.00)
    
    def __str__(self):
        return self.name if self.name else "Unnamed Portfolio"
    
    class Meta:
        verbose_name_plural = "Portfolios"

class Team(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=team_image_path,
        processors=[ResizeToFill(1333, 1694)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    image_png = models.ImageField(
        upload_to=team_png_image_path,
        null=True,
        blank=True,
    )  # New PNG image field
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _generate_unique_slug(self):
        """Generate a unique slug based on the name."""
        base_slug = slugify(self.name)
        slug = base_slug
        while Team.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        return slug
    
    def save(self, *args, **kwargs):
        # Only update slug if name has changed
        if self.pk:  # Check if the instance already exists
            original = Team.objects.get(pk=self.pk)
            if self.name != original.name:
                self.slug = self._generate_unique_slug()  # Update slug only if name is changed
        elif not self.slug:  # For new objects, generate a slug
            self.slug = self._generate_unique_slug()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name if self.name else "Unnamed Team Member"
    
    class Meta:
        verbose_name_plural = "Team Members"

class Contact(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Message from {self.name} - {self.subject}' if self.name and self.subject else "Unnamed Contact Message"
    
    class Meta:
        verbose_name_plural = "Contacts"

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
    email = models.EmailField(null=True, blank=True)
    second_email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure only one instance of settings can exist
        if not self.pk and Setting.objects.exists():
            raise ValueError("You can only create one instance of the settings.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Website Settings"
    
    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

class Blog(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
    ]

    title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs', null=True, blank=True)
    featured_image = ProcessedImageField(
        upload_to=blog_image_path,
        processors=[ResizeToFill(1200, 628)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    content = models.TextField(null=True, blank=True)
    excerpt = models.TextField(max_length=500, blank=True, null=True)
    tags = TaggableManager(blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _generate_random_number(self, length=6):
        """Generate a random number of specified length."""
        return ''.join(random.choices(string.digits, k=length))
    
    def _generate_unique_slug(self):
        """Generate a unique slug by appending 6 random numbers."""
        base_slug = slugify(self.title)
        random_number = self._generate_random_number()
        slug = f"{base_slug}-{random_number}"
        while Blog.objects.filter(slug=slug).exists():
            random_number = self._generate_random_number()
            slug = f"{base_slug}-{random_number}"
        return slug
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        if self.status == 'Published' and not self.published_at:
            self.published_at = timezone.now()
        super(Blog, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title if self.title else "Untitled Blog"
    
    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-published_at', '-created_at']

class Payment(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.portfolio:
            # Check if the payment status is 'Fully Paid' before saving the payment
            if self.portfolio.payment_status == "Fully Paid":
                # Instead of raising an error, raise a ValidationError to provide a user-friendly message
                raise ValidationError("Cannot record payment because the portfolio is already fully paid.")
        
        super().save(*args, **kwargs)
        
        if self.portfolio:
            # Update amount_paid in Portfolio
            total_paid = self.portfolio.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
            self.portfolio.amount_paid = total_paid
            self.portfolio.save()

            # Update PaymentStatus
            if self.portfolio.amount_paid >= (self.portfolio.project_amount or 0):
                PaymentStatus.objects.update_or_create(
                    payment=self,
                    defaults={'amount_paid': self.portfolio.amount_paid, 'status': 'Fully Paid'}
                )
            else:
                PaymentStatus.objects.update_or_create(
                    payment=self,
                    defaults={'amount_paid': self.portfolio.amount_paid, 'status': 'Partial'}
                )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

class PaymentStatus(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='statuses', null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='Partial', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status} for {self.payment}" if self.payment and self.status else "Unnamed Payment Status"

    class Meta:
        verbose_name = "Payment Status"
        verbose_name_plural = "Payment Statuses"

class Testimony(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='testimonies', null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Testimony from {self.client.name}" if self.client else "Unnamed Testimony"
    
    class Meta:
        verbose_name_plural = "Testimonies"

class PortfolioRepo(models.Model):
    """
    Model representing a repository link associated with a portfolio.
    This allows each Portfolio to have multiple repository links.
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='portfolio_repos'
    )
    link = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repo for {self.portfolio.name}: {self.link}"

class Training(models.Model):
    STATUS_CHOICES = [
        ('Coming Soon', 'Coming Soon'),
        ('Happening', 'Happening'),
        ('Ended', 'Ended'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = ProcessedImageField(
        upload_to=training_image_path,
        # processors=[ResizeToFill(1200, 675)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Coming Soon')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _generate_random_number(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    def _generate_unique_slug(self):
        base_slug = slugify(self.title)
        random_number = self._generate_random_number()
        slug = f"{base_slug}-{random_number}"
        while Training.objects.filter(slug=slug).exists():
            random_number = self._generate_random_number()
            slug = f"{base_slug}-{random_number}"
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Training"
        verbose_name_plural = "Trainings"
        ordering = ['-start_date']