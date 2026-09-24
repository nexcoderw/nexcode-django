from django.db import transaction

from home.models import Contact


def create_contact(
    cleaned_data,
    sender=None,
):
    contact = Contact(
        name=cleaned_data[
            "name"
        ],
        email=cleaned_data[
            "email"
        ],
        subject=cleaned_data[
            "subject"
        ],
        message=cleaned_data[
            "message"
        ],
        **(sender or {}),
    )

    with transaction.atomic():
        contact.save()

    return contact