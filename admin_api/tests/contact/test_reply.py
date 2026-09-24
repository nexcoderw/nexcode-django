from unittest import mock

from django.core import mail

from admin_api.tests.contact.base import (
    ContactApiTestCase,
)
from home.models import ContactReply


class ContactReplyTests(
    ContactApiTestCase
):
    def payload(
        self,
        **overrides,
    ):
        data = {
            "subject": (
                "Re: Project enquiry"
            ),
            "message": (
                "Thank you for reaching out.\n\n"
                "Could we meet on Monday?"
            ),
        }

        data.update(overrides)

        return data

    def test_authentication_is_required(
        self,
    ):
        contact = self.create_contact()

        response = self.post_json(
            self.reply_url(contact),
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_administrator_role_is_required(
        self,
    ):
        contact = self.create_contact()

        self.client.force_login(
            self.regular_user
        )

        response = self.post_json(
            self.reply_url(contact),
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_reply_emails_the_sender(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        response = self.post_json(
            self.reply_url(contact),
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            ["jane@example.com"],
        )

        self.assertEqual(
            email.subject,
            "Re: Project enquiry",
        )

        self.assertEqual(
            email.reply_to,
            ["nexcoderwa@gmail.com"],
        )

        self.assertIn(
            "Could we meet on Monday?",
            email.body,
        )

        html, mimetype = (
            email.alternatives[0]
        )

        self.assertEqual(
            mimetype,
            "text/html",
        )

        # Branded: an absolute logo URL, the greeting and the original
        # message for context.
        self.assertIn(
            "https://nexcode.africa/static/img/logo-w.png",
            html,
        )

        self.assertIn(
            "Hi Jane Doe,",
            html,
        )

        self.assertIn(
            "I would like to discuss a project.",
            html,
        )

    def test_reply_is_recorded_and_marks_the_message_answered(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        response = self.post_json(
            self.reply_url(contact),
            self.payload(),
        )

        reply = ContactReply.objects.get()

        self.assertEqual(
            reply.contact,
            contact,
        )

        self.assertEqual(
            reply.sent_by,
            self.admin_user,
        )

        contact.refresh_from_db()

        self.assertEqual(
            contact.replied_at,
            reply.sent_at,
        )

        data = response.json()[
            "data"
        ]

        self.assertIsNotNone(
            data["contact"][
                "replied_at"
            ]
        )

        self.assertEqual(
            data["reply"][
                "sent_by"
            ],
            "Ada Admin",
        )

    def test_later_replies_keep_the_first_reply_time(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        self.post_json(
            self.reply_url(contact),
            self.payload(),
        )

        contact.refresh_from_db()
        first_replied_at = (
            contact.replied_at
        )

        self.post_json(
            self.reply_url(contact),
            self.payload(
                message="A follow-up.",
            ),
        )

        contact.refresh_from_db()

        self.assertEqual(
            contact.replied_at,
            first_replied_at,
        )

        self.assertEqual(
            ContactReply.objects.count(),
            2,
        )

    def test_message_is_escaped_in_the_html_email(
        self,
    ):
        self.login_admin()
        contact = self.create_contact(
            name="<b>Jane</b>",
        )

        self.post_json(
            self.reply_url(contact),
            self.payload(
                message=(
                    "<script>alert(1)"
                    "</script>"
                ),
            ),
        )

        html = mail.outbox[0].alternatives[0][0]

        self.assertNotIn(
            "<script>alert(1)",
            html,
        )

        self.assertNotIn(
            "<b>Jane</b>",
            html,
        )

    def test_subject_and_message_are_required(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        for field in (
            "subject",
            "message",
        ):
            with self.subTest(
                field=field
            ):
                response = self.post_json(
                    self.reply_url(contact),
                    self.payload(
                        **{
                            field: "  ",
                        }
                    ),
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

                self.assertIn(
                    field,
                    response.json()[
                        "errors"
                    ],
                )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_multiline_subject_is_rejected(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        response = self.post_json(
            self.reply_url(contact),
            self.payload(
                subject=(
                    "Hello\nBcc: "
                    "victim@example.com"
                ),
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "subject",
            response.json()[
                "errors"
            ],
        )

    def test_failed_delivery_is_reported_and_not_recorded(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        with mock.patch(
            "django.core.mail.EmailMultiAlternatives.send",
            side_effect=OSError(
                "SMTP unavailable"
            ),
        ):
            response = self.post_json(
                self.reply_url(contact),
                self.payload(),
            )

        self.assertEqual(
            response.status_code,
            502,
        )

        self.assertFalse(
            ContactReply.objects.exists()
        )

        contact.refresh_from_db()

        self.assertIsNone(
            contact.replied_at
        )

    def test_unknown_contact_returns_not_found(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()
        url = self.reply_url(contact)
        contact.delete()

        response = self.post_json(
            url,
            self.payload(),
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_reply_requires_csrf(
        self,
    ):
        self.login_admin()
        contact = self.create_contact()

        response = self.client.post(
            self.reply_url(contact),
            data="{}",
            content_type=(
                "application/json"
            ),
        )

        self.assertEqual(
            response.status_code,
            403,
        )
