import os
import random
import string
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User  # Assuming you're using Django's built-in User model
from taggit.managers import TaggableManager
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.utils import timezone
from django.db.models import Sum

def portfolio_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'portfolio/work_{slugify(instance.name)}_{timestamp}{file_extension}'

def team_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'team/member_{slugify(instance.name)}_{timestamp}{file_extension}'

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

    # Existing Fields
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
    
    # New Fields
    repo_link = models.URLField(max_length=255, null=True, blank=True)
    figma_link = models.URLField(max_length=255, null=True, blank=True)
    project_category = models.CharField(max_length=255, choices=PROJECT_CATEGORY_CHOICES, null=True, blank=True)
    system_analysis_document = models.FileField(upload_to='portfolio/system_analysis/', null=True, blank=True)
    publish = models.BooleanField(default=False)
    
    # New Client Information Fields
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='portfolios', null=True, blank=True)
    
    # New Team Information Field
    team_members = models.ManyToManyField('Team', related_name='portfolios', blank=True)
    
    # New Document Field
    contract_document = models.FileField(upload_to='portfolio/contracts/', null=True, blank=True)
    
    # New Project Timeline Fields
    project_initiation_date = models.DateField(null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    
    # New Financial Fields
    project_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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
    position = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=team_image_path,
        processors=[ResizeToFill(1333, 1694)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
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
    
    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.portfolio}" if self.portfolio and self.amount_paid else "Unnamed Payment"
    
    def save(self, *args, **kwargs):
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
    status = models.CharField(max_length=20, default='Partial', null=True, blank=True)  # e.g., 'Partial', 'Fully Paid'
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.status} for {self.payment}" if self.payment and self.status else "Unnamed Payment Status"
    
    class Meta:
        verbose_name = "Payment Status"
        verbose_name_plural = "Payment Statuses"

class Testimony(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='testimonies')
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Testimony from {self.client.name}" if self.client else "Unnamed Testimony"
    
    class Meta:
        verbose_name_plural = "Testimonies"