import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import (
    Client as DjangoClient,
    TestCase,
)
from django.urls import reverse

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from home.models import (
    PaymentAgreement,
    PaymentInstallment,
    Portfolio,
)


class PaymentApiTestCase(
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
                    "payments@nexcode.africa"
                ),
                password=self.password,
            )
        )

        self.admin_user.groups.add(
            group
        )

        self.client = DjangoClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

        self.portfolio = (
            Portfolio.objects.create(
                name=(
                    "Payment Project"
                ),
                category=(
                    Portfolio.Category
                    .WEB_APPLICATION
                ),
                project_type=(
                    Portfolio
                    .ProjectType
                    .CLIENT_PROJECT
                ),
            )
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
                ][
                    "csrf_token"
                ],
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

    def patch_json(
        self,
        url,
        payload,
    ):
        return self.client.patch(
            url,
            data=json.dumps(
                payload
            ),
            content_type=(
                "application/json"
            ),
            **self.csrf_headers(),
        )

    def create_agreement(
        self,
        **overrides,
    ):
        values = {
            "portfolio":
                self.portfolio,

            "title":
                "Development Contract",

            "agreement_type":
                (
                    PaymentAgreement
                    .AgreementType
                    .PROJECT
                ),

            "currency":
                "RWF",

            "total_amount":
                Decimal(
                    "1000000.00"
                ),

            "agreement_date":
                date(
                    2026,
                    9,
                    1,
                ),

            "start_date":
                date(
                    2026,
                    9,
                    1,
                ),

            "status":
                (
                    PaymentAgreement
                    .Status.ACTIVE
                ),
        }

        values.update(
            overrides
        )

        return (
            PaymentAgreement
            .objects
            .create(
                **values
            )
        )

    def create_installment(
        self,
        agreement,
        **overrides,
    ):
        values = {
            "agreement":
                agreement,

            "sequence": 1,

            "title":
                "Installment 1",

            "installment_type":
                (
                    PaymentInstallment
                    .Type.INSTALLMENT
                ),

            "amount":
                Decimal(
                    "1000000.00"
                ),

            "due_type":
                (
                    PaymentInstallment
                    .DueType
                    .FIXED_DATE
                ),

            "expected_due_date":
                date(
                    2026,
                    10,
                    1,
                ),

            "due_date":
                date(
                    2026,
                    10,
                    1,
                ),
        }

        values.update(
            overrides
        )

        return (
            PaymentInstallment
            .objects
            .create(
                **values
            )
        )