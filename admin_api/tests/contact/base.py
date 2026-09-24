import json

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import (
    Client as DjangoClient,
    TestCase,
    override_settings,
)
from django.urls import reverse

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from home.models import Contact


@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends.locmem.EmailBackend"
    ),
    DEFAULT_FROM_EMAIL=(
        "NEXCODE <no-reply@nexcode.africa>"
    ),
    SITE_URL="https://nexcode.africa",
    STORAGES={
        "default": {
            "BACKEND": (
                "django.core.files.storage.FileSystemStorage"
            ),
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    },
)
class ContactApiTestCase(
    TestCase
):
    password = (
        "TestPassword123!"
    )

    def setUp(self):
        User = get_user_model()

        group, _ = (
            Group.objects.get_or_create(
                name=(
                    NEXCODE_ADMIN_GROUP_NAME
                )
            )
        )

        self.admin_user = (
            User.objects.create_user(
                username=(
                    "admin@nexcode.africa"
                ),
                email=(
                    "admin@nexcode.africa"
                ),
                password=self.password,
                first_name="Ada",
                last_name="Admin",
            )
        )

        self.admin_user.groups.add(
            group
        )

        self.regular_user = (
            User.objects.create_user(
                username=(
                    "user@nexcode.africa"
                ),
                email=(
                    "user@nexcode.africa"
                ),
                password=self.password,
            )
        )

        self.client = DjangoClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

        self.list_url = reverse(
            "admin_api:contact:list"
        )

    def login_admin(self):
        self.client.force_login(
            self.admin_user
        )

    def csrf_headers(self):
        response = self.client.get(
            self.csrf_url
        )

        return {
            "HTTP_X_CSRFTOKEN":
                response.json()[
                    "data"
                ]["csrf_token"],
        }

    def post_json(
        self,
        url,
        payload,
    ):
        return self.client.post(
            url,
            data=json.dumps(
                payload
            ),
            content_type=(
                "application/json"
            ),
            **self.csrf_headers(),
        )

    def detail_url(
        self,
        contact,
    ):
        return reverse(
            "admin_api:contact:detail",
            kwargs={
                "contact_id":
                    contact.pk,
            },
        )

    def reply_url(
        self,
        contact,
    ):
        return reverse(
            "admin_api:contact:reply",
            kwargs={
                "contact_id":
                    contact.pk,
            },
        )

    def create_contact(
        self,
        name="Jane Doe",
        **overrides,
    ):
        fields = {
            "name": name,
            "email": "jane@example.com",
            "subject": "Project enquiry",
            "message": (
                "I would like to "
                "discuss a project."
            ),
            "ip_address": "203.0.113.9",
            "user_agent": "Mozilla/5.0",
            "device_type":
                Contact.DeviceType.DESKTOP,
            "browser": "Chrome",
            "operating_system": "Windows",
        }

        fields.update(overrides)

        return Contact.objects.create(
            **fields
        )
