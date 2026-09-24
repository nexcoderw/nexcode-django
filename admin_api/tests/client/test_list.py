from admin_api.tests.client.base import (
    ClientApiTestCase,
)


class ClientListTests(
    ClientApiTestCase
):
    def setUp(self):
        super().setUp()

        self.create_client(
            name="Acme Rwanda",
            email="hello@acme.rw",
            phone_number=(
                "+250 788 000 000"
            ),
        )

        self.create_client(
            name="Bright Ventures",
            email="team@bright.co",
            phone_number=(
                "+254 700 111 222"
            ),
        )

    def names(
        self,
        response,
    ):
        return [
            item["name"]
            for item in response.json()[
                "data"
            ]["items"]
        ]

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

        self.assertEqual(
            response.json()["data"][
                "pagination"
            ]["total_items"],
            2,
        )

    def test_search_matches_name(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "bright",
            },
        )

        self.assertEqual(
            self.names(response),
            ["Bright Ventures"],
        )

    def test_search_matches_email(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "acme.rw",
            },
        )

        self.assertEqual(
            self.names(response),
            ["Acme Rwanda"],
        )

    def test_search_matches_phone_number(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "search": "+254",
            },
        )

        self.assertEqual(
            self.names(response),
            ["Bright Ventures"],
        )

    def test_ordering_is_supported(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering": "-name",
            },
        )

        self.assertEqual(
            self.names(response),
            [
                "Bright Ventures",
                "Acme Rwanda",
            ],
        )

    def test_invalid_ordering_is_rejected(
        self,
    ):
        self.login_admin()

        response = self.client.get(
            self.list_url,
            {
                "ordering": "status",
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
                "page_size": "500",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )
