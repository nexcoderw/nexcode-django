from django.contrib import admin
from django.urls import reverse
from django.utils.html import (
    format_html,
)

from home.models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "position",
        "slug",
        "linked_social_profiles",
        "created_at",
        "updated_at",
        "edit_link",
        "delete_link",
    )

    search_fields = (
        "name",
        "position",
        "linkedin",
        "github",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
        "pk",
    )

    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
    )

    list_per_page = 20

    def linked_social_profiles(
        self,
        obj,
    ):
        links = []

        if obj.linkedin:
            links.append(
                format_html(
                    '<a href="{}" '
                    'target="_blank" '
                    'rel="noopener noreferrer">'
                    "LinkedIn</a>",
                    obj.linkedin,
                )
            )

        if obj.github:
            links.append(
                format_html(
                    '<a href="{}" '
                    'target="_blank" '
                    'rel="noopener noreferrer">'
                    "GitHub</a>",
                    obj.github,
                )
            )

        if not links:
            return "-"

        return format_html(
            "{}",
            " | ".join(
                str(link)
                for link in links
            ),
        )

    linked_social_profiles.short_description = (
        "Social Profiles"
    )

    def edit_link(
        self,
        obj,
    ):
        url = reverse(
            "admin:home_team_change",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" '
            'href="{}">Edit</a>',
            url,
        )

    edit_link.short_description = (
        "Edit"
    )

    def delete_link(
        self,
        obj,
    ):
        url = reverse(
            "admin:home_team_delete",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" '
            'href="{}">Delete</a>',
            url,
        )

    delete_link.short_description = (
        "Delete"
    )