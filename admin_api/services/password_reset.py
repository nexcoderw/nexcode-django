import hashlib
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
    NEXCODE_ADMIN_PASSWORD_RESET_CODE_SECONDS,
    NEXCODE_ADMIN_PASSWORD_RESET_MAX_ATTEMPTS,
    NEXCODE_ADMIN_PASSWORD_RESET_TOKEN_SECONDS,
)
from admin_api.models import (
    AdminPasswordResetChallenge,
)
from admin_api.security.password_reset_throttle import (
    allow_password_reset_request,
)


def request_admin_password_reset(email):
    """
    Create and email an administrator recovery challenge.

    A random challenge ID is returned for unknown accounts so callers
    cannot determine whether the account exists from the response shape.
    """
    User = get_user_model()

    user = (
        User.objects.filter(
            username__iexact=email,
            email__iexact=email,
            is_active=True,
            groups__name=NEXCODE_ADMIN_GROUP_NAME,
        )
        .distinct()
        .first()
    )

    if user is None:
        return str(uuid.uuid4())

    if not allow_password_reset_request(email):
        existing = (
            AdminPasswordResetChallenge.objects.filter(
                user=user,
                consumed_at__isnull=True,
                verified_at__isnull=True,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if existing is not None:
            return str(existing.pk)

        return str(uuid.uuid4())

    now = timezone.now()

    code = (
        f"{secrets.randbelow(1_000_000):06d}"
    )

    with transaction.atomic():
        AdminPasswordResetChallenge.objects.filter(
            user=user,
            consumed_at__isnull=True,
        ).update(
            consumed_at=now,
        )

        challenge = (
            AdminPasswordResetChallenge.objects.create(
                user=user,
                code_hash=make_password(code),
                expires_at=(
                    now
                    + timedelta(
                        seconds=(
                            NEXCODE_ADMIN_PASSWORD_RESET_CODE_SECONDS
                        )
                    )
                ),
            )
        )

    try:
        _send_password_reset_code(
            user.email,
            code,
        )
    except Exception:
        challenge.consumed_at = (
            timezone.now()
        )
        challenge.save(
            update_fields=[
                "consumed_at",
            ]
        )

        raise

    return str(challenge.pk)


@transaction.atomic
def verify_admin_password_reset(
    challenge_id,
    code,
):
    """
    Consume a valid verification code and issue a one-time reset token.
    """
    try:
        challenge = (
            AdminPasswordResetChallenge.objects
            .select_for_update()
            .select_related("user")
            .get(pk=challenge_id)
        )
    except (
        AdminPasswordResetChallenge.DoesNotExist,
        ValueError,
    ):
        return None

    now = timezone.now()

    if not _challenge_can_be_verified(
        challenge,
        now,
    ):
        return None

    challenge.attempts += 1

    if not check_password(
        code,
        challenge.code_hash,
    ):
        update_fields = [
            "attempts",
        ]

        if (
            challenge.attempts
            >= NEXCODE_ADMIN_PASSWORD_RESET_MAX_ATTEMPTS
        ):
            challenge.consumed_at = now
            update_fields.append(
                "consumed_at"
            )

        challenge.save(
            update_fields=update_fields
        )

        return None

    reset_token = secrets.token_urlsafe(
        48
    )

    challenge.verified_at = now
    challenge.reset_expires_at = (
        now
        + timedelta(
            seconds=(
                NEXCODE_ADMIN_PASSWORD_RESET_TOKEN_SECONDS
            )
        )
    )
    challenge.reset_token_hash = (
        _hash_reset_token(reset_token)
    )

    challenge.save(
        update_fields=[
            "attempts",
            "verified_at",
            "reset_expires_at",
            "reset_token_hash",
        ]
    )

    return reset_token


@transaction.atomic
def confirm_admin_password_reset(
    reset_token,
    new_password,
):
    """
    Validate a reset token, change the password, and consume it.
    """
    token_hash = _hash_reset_token(
        reset_token
    )

    challenge = (
        AdminPasswordResetChallenge.objects
        .select_for_update()
        .select_related("user")
        .filter(
            reset_token_hash=token_hash,
        )
        .first()
    )

    now = timezone.now()

    if (
        challenge is None
        or challenge.verified_at is None
        or challenge.consumed_at is not None
        or challenge.reset_expires_at is None
        or challenge.reset_expires_at
        <= now
    ):
        return False

    user = challenge.user

    if (
        not user.is_active
        or not user.groups.filter(
            name=NEXCODE_ADMIN_GROUP_NAME,
        ).exists()
    ):
        return False

    validate_password(
        new_password,
        user=user,
    )

    user.set_password(
        new_password
    )
    user.save(
        update_fields=[
            "password",
        ]
    )

    challenge.consumed_at = now
    challenge.reset_token_hash = None

    challenge.save(
        update_fields=[
            "consumed_at",
            "reset_token_hash",
        ]
    )

    AdminPasswordResetChallenge.objects.filter(
        user=user,
        consumed_at__isnull=True,
    ).exclude(
        pk=challenge.pk,
    ).update(
        consumed_at=now,
    )

    return True


def _challenge_can_be_verified(
    challenge,
    now,
):
    user = challenge.user

    return (
        challenge.consumed_at is None
        and challenge.verified_at is None
        and challenge.expires_at > now
        and challenge.attempts
        < NEXCODE_ADMIN_PASSWORD_RESET_MAX_ATTEMPTS
        and user.is_active
        and user.groups.filter(
            name=NEXCODE_ADMIN_GROUP_NAME,
        ).exists()
    )


def _hash_reset_token(token):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def _send_password_reset_code(
    email,
    code,
):
    minutes = (
        NEXCODE_ADMIN_PASSWORD_RESET_CODE_SECONDS
        // 60
    )

    send_mail(
        subject=(
            "Your NEXCODE admin "
            "password reset code"
        ),
        message=(
            "A password reset was requested "
            "for your NEXCODE administrator "
            "account.\n\n"
            f"Verification code: {code}\n\n"
            f"This code expires in {minutes} "
            "minutes.\n\n"
            "If you did not request this, "
            "you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            email,
        ],
        fail_silently=False,
    )