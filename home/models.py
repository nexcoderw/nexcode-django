import os
import random
import string
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

def portfolio_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'portfolio/work_{slugify(instance.name)}_{instance.created_at.strftime("%Y%m%d%H%M%S")}{file_extension}'

class Portfolio(models.Model):
    CATEGORY_CHOICES = [
        ('Web App', 'Web App'),
        ('Logo', 'Logo'),
        ('UI/UX', 'UI/UX'),
        ('Mobile App', 'Mobile App'),
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
    
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_email = models.EmailField(null=True, blank=True)
    client_phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    team_members = models.ManyToManyField('Team', related_name='portfolios', blank=True)
    
    contract_document = models.FileField(upload_to='portfolio/contracts/', null=True, blank=True)
    
    project_initiation_date = models.DateField(null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    
    project_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    
    def __str__(self):
        return self.name if self.name else "Unnamed Portfolio"
    
    class Meta:
        verbose_name_plural = "Portfolios"

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

def blog_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'blog/{slugify(instance.title)}_{instance.created_at}{file_extension}'

class Blog(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    featured_image = ProcessedImageField(
        upload_to=blog_image_path,
        processors=[ResizeToFill(1200, 628)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    tags = TaggableManager()
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
            from django.utils import timezone
            self.published_at = timezone.now()
        super(Blog, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-published_at', '-created_at']
