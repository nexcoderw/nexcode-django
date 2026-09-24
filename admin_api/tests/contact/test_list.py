from django.utils import timezone

from admin_api.tests.contact.base import (
    ContactApiTestCase,
)


class ContactListTests(
    ContactApiTestCase
):
    def test_authentication_is_required(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_administrator_role_is_required(
        self,
    ):
        self.client.force_login(
            self.regular_user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_lists_contacts_with_sender_details(
        self,
    ):
        self.login_admin()
        self.create_contact()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Cache-Control"],
            "no-store",
        )

        data = response.json()[
            "data"
        ]

        item = data["items"][0]

        self.assertEqual(
            set(item),
            {
                "id",
                "name",
                "email",
                "subject",
                "message",
                "created_at",
                "ip_address",
                "user_agent",
                "device_type",
                "browser",
                "operating_system",
                "replied_at",
            },
        )

        self.assertEqual(
            item["ip_address"],
            "203.0.113.9",
        )

        self.assertEqual(
            item["device_type"],
            "desktop",
        )

        self.assertEqual(
            data["pagination"][
                "total_items"
            ],
            1,
        )

        self.assertEqual(
            data["unanswered"],
            1,
        )

    def test_newest_messages_come_first(
        self,
    ):
        self.login_admin()

        first = self.create_contact(
            "First"
        )

        second = self.create_contact(
            "Second"
        )

        ids = [
            item["id"]
            for item in self.client.get(
                self.list_url
            ).json()["data"]["items"]
        ]

        self.assertEqual(
            ids,
            [
                second.pk,
                first.pk,
            ],
        )

    def test_search_matches_name_email_subject_and_address(
        self,
    ):
        self.login_admin()

        self.create_contact(
            "Jane Doe"
        )

        self.create_contact(
            "John Smith",
            email="john@acme.rw",
            subject="Support request",
            ip_address="198.51.100.4",
        )

        for search, expected in (
            ("jane", "Jane Doe"),
            ("acme.rw", "John Smith"),
            ("support", "John Smith"),
            ("198.51", "John Smith"),
        ):
            with self.subTest(
                search=search
            ):
                items = self.client.get(
                    self.list_url,
                    {
                        "search":
                            search,
                    },
                ).json()["data"]["items"]

                self.assertEqual(
                    [
                        item["name"]
                        for item in items
                    ],
                    [expected],
                )

    def test_status_filter_splits_new_and_replied(
        self,
    ):
        self.login_admin()

        self.create_contact(
            "Waiting"
        )

        self.create_contact(
            "Answered",
            replied_at=timezone.now(),
        )

        for status, expected in (
            ("new", "Waiting"),
            ("replied", "Answered"),
        ):
            with self.subTest(
                status=status
            ):
                items = self.client.get(
                    self.list_url,
                    {
                        "status":
                            status,
                    },
                ).json()["data"]["items"]

                self.assertEqual(
                    [
                        item["name"]
                        for item in items
                    ],
                    [expected],
                )

    def test_invalid_filters_are_rejected(
        self,
    ):
        self.login_admin()

        for params in (
            {"status": "spam"},
            {"ordering": "ip_address"},
            {"page": "0"},
        ):
            with self.subTest(
                params=params
            ):
                response = self.client.get(
                    self.list_url,
                    params,
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

    def test_post_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            self.list_url,
            {},
        )

        self.assertEqual(
            response.status_code,
            405,
        )
