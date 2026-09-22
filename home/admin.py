from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from home.models import Contact, Setting, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'slug', 'linked_social_profiles', 'edit_link', 'delete_link')
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

