from home.models import *
from django.contrib import admin

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow adding only if there is no existing Setting instance
        return not Setting.objects.exists()

    list_display = ('address', 'email', 'phone_number')