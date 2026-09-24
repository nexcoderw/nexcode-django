import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone

from home.content import CONTACT_DETAILS
from home.models import ContactReply
from home.seo import absolute_url


logger = logging.getLogger(__name__)


class ContactReplyNotSent(
    Exception
):
    """The reply email could not be handed to the mail server."""


def send_contact_reply(
    contact,
    cleaned_data,
    admin_user,
):
    """Email a reply to the sender, then record it.

    The reply is only saved once the email has gone out, so the history
    never lists a reply the sender did not receive.
    """
    subject = cleaned_data["subject"]
    message = cleaned_data["message"]

    try:
        _build_email(
            contact,
            subject,
            message,
        ).send(
            fail_silently=False,
        )
    except Exception as error:
        logger.error(
            "Contact reply email failed.",
            extra={
                "contact_id": contact.pk,
                "error": type(error).__name__,
            },
        )

        raise ContactReplyNotSent from error

    with transaction.atomic():
        reply = ContactReply.objects.create(
            contact=contact,
            subject=subject,
            message=message,
            sent_by=admin_user,
        )

        # The first reply marks the message answered; later replies keep
        # that original time.
        if contact.replied_at is None:
            contact.replied_at = reply.sent_at
            contact.save(
                update_fields=[
                    "replied_at",
                ]
            )

    return reply


def _build_email(
    contact,
    subject,
    message,
):
    context = {
        "contact": contact,
        "subject": subject,
        "message": message,
        "details": CONTACT_DETAILS,
        "site_url": settings.SITE_URL,
        # Mail clients load images from the public site, so the logo
        # needs an absolute URL. PNG, as many clients drop SVG.
        "logo_url": absolute_url(
            static("img/logo-w.png")
        ),
        "year": timezone.now().year,
    }

    email = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(
            "emails/contact_reply.txt",
            context,
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contact.email],
        # Answers from the sender reach the team inbox, not a no-reply
        # sending address.
        reply_to=[CONTACT_DETAILS["email"]],
    )

    email.attach_alternative(
        render_to_string(
            "emails/contact_reply.html",
            context,
        ),
        "text/html",
    )

    return email
