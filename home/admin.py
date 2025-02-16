from django import forms
from home.models import *
from django.contrib import admin
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'edit_link', 'delete_link')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 20

    def edit_link(self, obj):
        url = reverse("admin:home_client_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_client_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

# Inline for Payments in Portfolio Admin
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    readonly_fields = ('payment_date',)
    fields = ('amount_paid', 'payment_date')
    show_change_link = True

# Inline for PaymentStatus in Payment Admin
class PaymentStatusInline(admin.TabularInline):
    model = PaymentStatus
    extra = 0
    readonly_fields = ('amount_paid', 'status', 'updated_at')
    fields = ('amount_paid', 'status', 'updated_at')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'client_info', 'project_category', 'publish', 'project_amount', 'amount_paid', 'edit_link', 'delete_link')
    search_fields = ('name', 'description', 'client__name', 'client__email', 'client__phone_number')
    list_filter = ('category', 'created_at', 'tags', 'project_category', 'publish')
    ordering = ('-created_at',)
    inlines = [PaymentInline]
    list_per_page = 20
    
    def client_info(self, obj):
        return f"{obj.client.name if obj.client else '-'} | {obj.client.phone_number if obj.client else '-'}"
    client_info.short_description = 'Client Information'

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'

    def project_category(self, obj):
        return obj.get_project_category_display() if obj.project_category else '-'
    project_category.short_description = 'Project Category'

    def edit_link(self, obj):
        url = reverse("admin:home_portfolio_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_portfolio_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'linked_social_profiles', 'edit_link', 'delete_link')
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
    
    def edit_link(self, obj):
        url = reverse("admin:home_team_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_team_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'edit_link', 'delete_link')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_per_page = 20
    
    def edit_link(self, obj):
        url = reverse("admin:home_contact_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_contact_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

class BlogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Blog
        fields = '__all__'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ('title', 'author', 'status', 'published_at', 'created_at', 'display_tags', 'edit_link', 'delete_link')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    list_filter = ('status', 'created_at', 'published_at', 'tags', 'category', 'author')
    ordering = ('-published_at', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
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
    
    def edit_link(self, obj):
        url = reverse("admin:home_blog_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_blog_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow adding only if there is no existing Setting instance
        return not Setting.objects.exists()
    
    list_display = ('address', 'email', 'phone_number', 'edit_link', 'delete_link')
    readonly_fields = ('created_at',)
    list_per_page = 20
    
    def edit_link(self, obj):
        url = reverse("admin:home_setting_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_setting_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount_paid', 'payment_date', 'edit_link', 'delete_link')
    search_fields = ('portfolio__name', 'amount_paid')
    list_filter = ('payment_date',)
    ordering = ('-payment_date',)
    inlines = [PaymentStatusInline]
    list_per_page = 20
    
    def edit_link(self, obj):
        url = reverse("admin:home_payment_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_payment_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payment', 'amount_paid', 'status', 'updated_at', 'edit_link', 'delete_link')
    search_fields = ('payment__portfolio__name', 'status')
    list_filter = ('status', 'updated_at')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)
    list_per_page = 20
    
    def edit_link(self, obj):
        url = reverse("admin:home_paymentstatus_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_paymentstatus_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"

@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    list_display = ('client', 'message', 'edit_link', 'delete_link')
    search_fields = ('client__name', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    def edit_link(self, obj):
        url = reverse("admin:home_testimony_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)
    edit_link.short_description = "Edit"
    
    def delete_link(self, obj):
        url = reverse("admin:home_testimony_delete", args=[obj.pk])
        return format_html('<a class="button" href="{}">Delete</a>', url)
    delete_link.short_description = "Delete"