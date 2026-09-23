from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase

from home.models import Client


class ClientModelTests(
    TestCase
):
    def create_client(
        self,
        **overrides,
    ):
        values = {
            "name":
                "GRACON Tech Holdings",
        }

        values.update(
            overrides
        )

        return (
            Client.objects.create(
                **values
            )
        )

    def test_slug_is_generated(
        self,
    ):
        client = (
            self.create_client()
        )

        self.assertEqual(
            client.slug,
            "gracon-tech-holdings",
        )

    def test_slug_remains_stable_after_rename(
        self,
    ):
        client = (
            self.create_client()
        )

        original_slug = (
            client.slug
        )

        client.name = (
            "GRACON Technologies"
        )

        client.save()

        client.refresh_from_db()

        self.assertEqual(
            client.slug,
            original_slug,
        )

    def test_duplicate_names_receive_unique_slugs(
        self,
    ):
        first = (
            self.create_client()
        )

        second = (
            self.create_client()
        )

        self.assertNotEqual(
            first.slug,
            second.slug,
        )

        self.assertTrue(
            second.slug.startswith(
                "gracon-tech-holdings-"
            )
        )

    def test_status_defaults_to_active(
        self,
    ):
        client = (
            self.create_client()
        )

        self.assertEqual(
            client.status,
            Client.Status.ACTIVE,
        )

    def test_optional_fields_can_be_empty(
        self,
    ):
        client = (
            self.create_client()
        )

        self.assertEqual(
            client.company_name,
            "",
        )

        self.assertEqual(
            client.email,
            "",
        )

        self.assertEqual(
            client.phone,
            "",
        )

        self.assertEqual(
            client.website,
            "",
        )

        self.assertEqual(
            client.location,
            "",
        )

        self.assertEqual(
            client.notes,
            "",
        )

        self.assertFalse(
            client.profile_image
        )

    def test_invalid_status_is_rejected_by_database(
        self,
    ):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                self.create_client(
                    status="unknown",
                )