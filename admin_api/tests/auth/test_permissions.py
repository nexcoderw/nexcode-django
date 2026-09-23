from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.http import JsonResponse
from django.test import RequestFactory, TestCase

from admin_api.constants import NEXCODE_ADMIN_GROUP_NAME
from admin_api.permissions import is_nexcode_admin, nexcode_admin_required


class NexcodeAdminPermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # The group is created by a migration, so it already exists in
        # the test database.
        self.group, _ = Group.objects.get_or_create(
            name=NEXCODE_ADMIN_GROUP_NAME,
        )

        User = get_user_model()

        self.admin_user = User.objects.create_user(
            username="admin@nexcode.africa",
            email="admin@nexcode.africa",
            password="TestPassword123!",
        )
        self.admin_user.groups.add(self.group)

        self.regular_user = User.objects.create_user(
            username="user@nexcode.africa",
            email="user@nexcode.africa",
            password="TestPassword123!",
        )

    def test_group_member_is_nexcode_admin(self):
        self.assertTrue(
            is_nexcode_admin(self.admin_user)
        )

    def test_regular_user_is_not_nexcode_admin(self):
        self.assertFalse(
            is_nexcode_admin(self.regular_user)
        )

    def test_anonymous_user_is_not_nexcode_admin(self):
        self.assertFalse(
            is_nexcode_admin(AnonymousUser())
        )

    def test_inactive_group_member_is_not_nexcode_admin(self):
        self.admin_user.is_active = False
        self.admin_user.save(
            update_fields=["is_active"]
        )

        self.assertFalse(
            is_nexcode_admin(self.admin_user)
        )

    def test_decorator_rejects_anonymous_request(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_decorator_rejects_non_admin_user(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = self.regular_user

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_decorator_allows_nexcode_admin(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = self.admin_user

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            200,
        )

