from datetime import date

from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase

from home.models import (
    Portfolio,
    PortfolioImage,
    PortfolioRepository,
    Team,
)


class PortfolioModelTests(
    TestCase
):
    def create_portfolio(
        self,
        **overrides,
    ):
        values = {
            "name":
                "NEXCODE Admin",
            "category": (
                Portfolio.Category
                .WEB_APPLICATION
            ),
            "project_type": (
                Portfolio.ProjectType
                .CLIENT_PROJECT
            ),
        }

        values.update(
            overrides
        )

        return (
            Portfolio.objects.create(
                **values
            )
        )

    def test_slug_is_generated(
        self,
    ):
        portfolio = (
            self.create_portfolio()
        )

        self.assertEqual(
            portfolio.slug,
            "nexcode-admin",
        )

    def test_slug_remains_stable_after_rename(
        self,
    ):
        portfolio = (
            self.create_portfolio()
        )

        original_slug = (
            portfolio.slug
        )

        portfolio.name = (
            "NEXCODE Platform"
        )

        portfolio.save()

        portfolio.refresh_from_db()

        self.assertEqual(
            portfolio.slug,
            original_slug,
        )

    def test_duplicate_names_receive_unique_slugs(
        self,
    ):
        first = (
            self.create_portfolio()
        )

        second = (
            self.create_portfolio()
        )

        self.assertNotEqual(
            first.slug,
            second.slug,
        )

        self.assertTrue(
            second.slug.startswith(
                "nexcode-admin-"
            )
        )

    def test_team_members_can_be_assigned(
        self,
    ):
        member = (
            Team.objects.create(
                name="Example Developer",
                position="Developer",
            )
        )

        portfolio = (
            self.create_portfolio()
        )

        portfolio.team_members.add(
            member
        )

        self.assertTrue(
            portfolio.team_members
            .filter(
                pk=member.pk
            )
            .exists()
        )

    def test_publishing_sets_published_at(
        self,
    ):
        portfolio = (
            self.create_portfolio(
                status=(
                    Portfolio.Status
                    .PUBLISHED
                )
            )
        )

        self.assertIsNotNone(
            portfolio.published_at
        )

    def test_draft_has_no_published_at(
        self,
    ):
        portfolio = (
            self.create_portfolio(
                status=(
                    Portfolio.Status
                    .PUBLISHED
                )
            )
        )

        portfolio.status = (
            Portfolio.Status.DRAFT
        )

        portfolio.save()

        portfolio.refresh_from_db()

        self.assertIsNone(
            portfolio.published_at
        )

    def test_deadline_cannot_precede_start_date(
        self,
    ):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                self.create_portfolio(
                    project_initiation_date=(
                        date(
                            2026,
                            9,
                            20,
                        )
                    ),
                    deadline_date=(
                        date(
                            2026,
                            9,
                            19,
                        )
                    ),
                )

    def test_only_one_cover_image_is_allowed(
        self,
    ):
        portfolio = (
            self.create_portfolio()
        )

        PortfolioImage.objects.create(
            portfolio=portfolio,
            image=(
                "portfolios/"
                "first.jpg"
            ),
            is_cover=True,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                PortfolioImage.objects.create(
                    portfolio=portfolio,
                    image=(
                        "portfolios/"
                        "second.jpg"
                    ),
                    is_cover=True,
                )

    def test_repository_url_is_unique_per_portfolio(
        self,
    ):
        portfolio = (
            self.create_portfolio()
        )

        url = (
            "https://github.com/"
            "nexcoderw/example"
        )

        PortfolioRepository.objects.create(
            portfolio=portfolio,
            label="GitHub",
            url=url,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                PortfolioRepository.objects.create(
                    portfolio=portfolio,
                    label="Source",
                    url=url,
                )