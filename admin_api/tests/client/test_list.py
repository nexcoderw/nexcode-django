from home.models import Client

from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientListTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        Client.objects.create(
            name="Alpha Client",
            company_name="Alpha Ltd",
            email="alpha@example.com",
            status=Client.Status.ACTIVE,
        )

        Client.objects.create(
            name="Beta Client",
            company_name="Beta Ltd",
            email="beta@example.com",
            status=(
                Client.Status.INACTIVE
            ),
        )

    def test_list_requires_authentication(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_list_rejects_non_admin(
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

    def test_admin_can_list_clients(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()[
            "data"
        ]

        self.assertEqual(
            data["pagination"][
                "total_items"
            ],
            2,
        )

    def test_search_filters_clients(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "Beta",
            },
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            len(items),
            1,
        )

        self.assertEqual(
            items[0]["name"],
            "Beta Client",
        )

    def test_status_filters_clients(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "status": "inactive",
            },
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            len(items),
            1,
        )

        self.assertEqual(
            items[0]["status"],
            "inactive",
        )

    def test_ordering_is_supported(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering": "name",
            },
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            [
                item["name"]
                for item in items
            ],
            [
                "Alpha Client",
                "Beta Client",
            ],
        )

    def test_invalid_status_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "status": "unknown",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_invalid_ordering_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering":
                    "secret_field",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_page_size_is_bounded(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "page_size": 101,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )