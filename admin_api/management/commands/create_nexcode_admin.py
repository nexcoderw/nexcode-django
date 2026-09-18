from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


ADMIN_GROUP_NAME = "NEXCODE_ADMIN"


class Command(BaseCommand):
    help = "Create a Django user with access to the NEXCODE admin portal."

    def handle(self, *args, **options):
        User = get_user_model()

        email = self._prompt_email(User)
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()

        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        password = self._prompt_password(user)

        try:
            admin_group = Group.objects.get(
                name=ADMIN_GROUP_NAME,
            )
        except Group.DoesNotExist as error:
            raise CommandError(
                f"{ADMIN_GROUP_NAME} does not exist. "
                "Run the admin_api migrations first."
            ) from error

        with transaction.atomic():
            user.set_password(password)
            user.save()
            user.groups.add(admin_group)

        self.stdout.write(
            self.style.SUCCESS(
                f"NEXCODE administrator created: {user.email}"
            )
        )

    def _prompt_email(self, User):
        while True:
            email = input("Email: ").strip().lower()

            if not email:
                self.stderr.write(
                    self.style.ERROR(
                        "Email is required."
                    )
                )
                continue

            if User.objects.filter(
                username__iexact=email,
            ).exists():
                self.stderr.write(
                    self.style.ERROR(
                        "A user with this email already exists."
                    )
                )
                continue

            if User.objects.filter(
                email__iexact=email,
            ).exists():
                self.stderr.write(
                    self.style.ERROR(
                        "A user with this email already exists."
                    )
                )
                continue

            return email

    def _prompt_password(self, user):
        while True:
            password = getpass("Password: ")

            if not password:
                self.stderr.write(
                    self.style.ERROR(
                        "Password is required."
                    )
                )
                continue

            confirmation = getpass(
                "Confirm password: "
            )

            if password != confirmation:
                self.stderr.write(
                    self.style.ERROR(
                        "Passwords do not match."
                    )
                )
                continue

            try:
                validate_password(
                    password,
                    user=user,
                )
            except ValidationError as error:
                for message in error.messages:
                    self.stderr.write(
                        self.style.ERROR(message)
                    )

                continue

            return password