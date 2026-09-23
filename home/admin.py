from django.contrib import admin
from django.urls import reverse
from django.utils.html import (
    format_html,
)

from django.db.models import Count

from home.models import (
    Portfolio,
    PortfolioDocument,
    PortfolioImage,
    PortfolioRepository,
    Team,
)


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

class PortfolioImageInline(
    admin.TabularInline
):
    model = PortfolioImage
    extra = 0

    fields = (
        "image",
        "alt_text",
        "is_cover",
        "position",
    )


class PortfolioDocumentInline(
    admin.TabularInline
):
    model = PortfolioDocument
    extra = 0

    fields = (
        "title",
        "document_type",
        "file",
    )


class PortfolioRepositoryInline(
    admin.TabularInline
):
    model = PortfolioRepository
    extra = 0

    fields = (
        "label",
        "url",
    )


@admin.register(Portfolio)
class PortfolioAdmin(
    admin.ModelAdmin
):
    list_display = (
        "name",
        "category",
        "project_type",
        "status",
        "team_member_count",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "summary",
        "description",
        "slug",
    )

    list_filter = (
        "category",
        "project_type",
        "status",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "slug",
        "published_at",
        "created_at",
        "updated_at",
    )

    filter_horizontal = (
        "team_members",
    )

    list_per_page = 20

    inlines = (
        PortfolioImageInline,
        PortfolioDocumentInline,
        PortfolioRepositoryInline,
    )

    def get_queryset(
        self,
        request,
    ):
        return (
            super()
            .get_queryset(request)
            .annotate(
                _team_member_count=Count(
                    "team_members",
                    distinct=True,
                )
            )
        )

    @admin.display(
        description="Team members",
        ordering="_team_member_count",
    )
    def team_member_count(
        self,
        obj,
    ):
        return (
            obj._team_member_count
        )