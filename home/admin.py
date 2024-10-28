from home.models import *
from django.contrib import admin

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

    # Optional: Make the fields read-only except for the message field if needed
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow adding only if there is no existing Setting instance
        return not Setting.objects.exists()

    list_display = ('address', 'email', 'phone_number')