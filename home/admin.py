from django import forms
from home.models import *
from django.urls import reverse
from django.contrib import admin
from django.utils.http import urlencode
from django.utils.html import format_html
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    readonly_fields = ('payment_date',)
    fields = ('amount_paid', 'payment_date', 'view_payment')
    
    def view_payment(self, obj):
        if obj.pk:
            url = reverse("admin:home_payment_change", args=[obj.pk])
            return format_html('<a class="button" href="{}">View</a>', url)
        return "-"
    view_payment.short_description = "View Payment"

class PaymentStatusInline(admin.TabularInline):
    model = PaymentStatus
    extra = 1
    readonly_fields = ('updated_at',)
    fields = ('amount_paid', 'status', 'updated_at')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'client_info', 'project_amount', 'amount_paid', 'created_at', 'updated_at', 'display_tags', 'view_portfolio')
    search_fields = ('name', 'description', 'client_name', 'client_email', 'client_phone_number')
    list_filter = ('category', 'created_at', 'tags')
    ordering = ('-created_at',)
    inlines = [PaymentInline]
    list_per_page = 20
    
    def client_info(self, obj):
        return f"{obj.client_name} | {obj.client_email} | {obj.client_phone_number}"
    client_info.short_description = 'Client Information'
    
    def view_portfolio(self, obj):
        url = reverse("admin:home_portfolio_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_portfolio.short_description = "View"
    
    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'linked_social_profiles', 'created_at', 'updated_at', 'view_team')
    search_fields = ('name', 'position', 'linkedin', 'github')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 20
    
    def linked_social_profiles(self, obj):
        links = []
        if obj.linkedin:
            links.append(f'<a href="{obj.linkedin}" target="_blank">LinkedIn</a>')
        if obj.github:
            links.append(f'<a href="{obj.github}" target="_blank">GitHub</a>')
        return format_html(" | ".join(links)) if links else "-"
    linked_social_profiles.short_description = 'Social Profiles'
    linked_social_profiles.allow_tags = True
    
    def view_team(self, obj):
        url = reverse("admin:home_team_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_team.short_description = "View"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'view_contact')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_per_page = 20
    
    def view_contact(self, obj):
        url = reverse("admin:home_contact_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_contact.short_description = "View"

class BlogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Blog
        fields = '__all__'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ('title', 'author', 'status', 'published_at', 'created_at', 'display_tags', 'view_blog')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    list_filter = ('status', 'created_at', 'published_at', 'tags', 'category', 'author')
    ordering = ('-published_at', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    inlines = []
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('featured_image', 'content', 'excerpt'),
        }),
        ('Meta', {
            'fields': ('tags', 'category'),
        }),
        ('Publication', {
            'fields': ('published_at',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'
    
    def view_blog(self, obj):
        url = reverse("admin:home_blog_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_blog.short_description = "View"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Setting.objects.exists()

    list_display = ('address', 'email', 'phone_number', 'view_setting')
    readonly_fields = ('created_at',)
    list_per_page = 20
    
    def view_setting(self, obj):
        url = reverse("admin:home_setting_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_setting.short_description = "View"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount_paid', 'payment_date', 'view_payment')
    search_fields = ('portfolio__name', 'amount_paid')
    list_filter = ('payment_date',)
    ordering = ('-payment_date',)
    inlines = [PaymentStatusInline]
    list_per_page = 20
    
    def view_payment(self, obj):
        url = reverse("admin:home_payment_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_payment.short_description = "View"

@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payment', 'amount_paid', 'status', 'updated_at', 'view_status')
    search_fields = ('payment__portfolio__name', 'status')
    list_filter = ('status', 'updated_at')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)
    list_per_page = 20
    
    def view_status(self, obj):
        url = reverse("admin:home_paymentstatus_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)
    view_status.short_description = "View"
