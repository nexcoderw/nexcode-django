from home.models import ContactReply

from admin_api.tests.contact.base import (
    ContactApiTestCase,
)


class ContactDetailTests(
    ContactApiTestCase
):
    def test_authentication_is_required(
        self,
    ):
        contact = self.create_contact()

        response = self.client.get(
            self.detail_url(contact)
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_detail_includes_reply_history(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        ContactReply.objects.create(
            contact=contact,
            subject="Re: Project enquiry",
            message="Thanks, Jane.",
            sent_by=self.admin_user,
        )

        response = self.client.get(
            self.detail_url(contact)
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()[
            "data"
        ]

        self.assertEqual(
            data["contact"]["id"],
            contact.pk,
        )

        self.assertEqual(
            [
                reply["message"]
                for reply in data[
                    "replies"
                ]
            ],
            ["Thanks, Jane."],
        )

        self.assertEqual(
            data["replies"][0][
                "sent_by"
            ],
            "Ada Admin",
        )

    def test_unknown_contact_returns_not_found(
        self,
    ):
        self.login_admin()

        contact = self.create_contact()
        url = self.detail_url(contact)
        contact.delete()

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            404,
        )
