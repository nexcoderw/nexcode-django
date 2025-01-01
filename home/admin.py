from django import forms
from home.models import *
from django.contrib import admin
from ckeditor_uploader.widgets import CKEditorUploadingWidget

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'updated_at', 'display_tags')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'

    readonly_fields = ('created_at', 'updated_at')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'created_at', 'updated_at')
    search_fields = ('name', 'position')
    list_filter = ('created_at', 'updated_at')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

class BlogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Blog
        fields = '__all__'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ('title', 'author', 'status', 'published_at', 'created_at', 'display_tags')
    search_fields = ('title', 'content', 'excerpt')
    list_filter = ('status', 'created_at', 'published_at', 'tags', 'category', 'author')
    ordering = ('-published_at', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')

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
    
    # Optional: Add filters for the admin list view
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow adding only if there is no existing Setting instance
        return not Setting.objects.exists()

    list_display = ('address', 'email', 'phone_number')