from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from home.models import Client


class ClientModelTests(
    TestCase
):
    def test_contact_details_can_be_empty(
        self,
    ):
        client = Client.objects.create(
            name="Walk-in client",
        )

        client.full_clean()

        self.assertEqual(
            client.email,
            "",
        )

        self.assertEqual(
            client.phone_number,
            "",
        )

    def test_string_is_the_name(
        self,
    ):
        client = Client(
            name="Acme Rwanda",
        )

        self.assertEqual(
            str(client),
            "Acme Rwanda",
        )

    def test_newest_clients_come_first(
        self,
    ):
        older = Client.objects.create(
            name="Older",
        )

        newer = Client.objects.create(
            name="Newer",
        )

        # created_at is auto-set, so move the first one back explicitly
        # rather than relying on two inserts landing at different times.
        Client.objects.filter(
            pk=older.pk
        ).update(
            created_at=(
                timezone.now()
                - timedelta(days=1)
            )
        )

        self.assertEqual(
            list(
                Client.objects.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [
                newer.pk,
                older.pk,
            ],
        )
