from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.permissions import IsAdmin

PASSWORD = "Kata-Sandi-Kuat-2026"


class AdminOnlyView(APIView):
    """View contoh untuk menguji IsAdmin lewat alur permintaan yang lengkap."""

    permission_classes = (IsAdmin,)

    def get(self, request):
        return Response({"ok": True})


class IsAdminTests(TestCase):
    def setUp(self):
        self.permission = IsAdmin()
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password=PASSWORD,
            name="Admin",
        )
        self.admin.role = User.Role.ADMIN
        self.admin.save()

    def has_permission(self, user):
        return self.permission.has_permission(SimpleNamespace(user=user), None)

    def get_view(self, user=None):
        headers = {}
        if user is not None:
            access = RefreshToken.for_user(user).access_token
            headers["HTTP_AUTHORIZATION"] = f"Bearer {access}"
        request = APIRequestFactory().get("/", **headers)
        return AdminOnlyView.as_view()(request)

    def test_anonymous_user_is_denied(self):
        self.assertFalse(self.has_permission(AnonymousUser()))

    def test_regular_user_is_denied(self):
        self.assertFalse(self.has_permission(self.user))

    def test_admin_is_allowed(self):
        self.assertTrue(self.has_permission(self.admin))

    def test_view_without_token_returns_401(self):
        response = self.get_view()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_with_regular_user_returns_403(self):
        response = self.get_view(self.user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_with_admin_returns_200(self):
        response = self.get_view(self.admin)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"ok": True})

    def test_demoted_admin_loses_access_immediately(self):
        access_view = self.get_view(self.admin)
        self.admin.role = User.Role.USER
        self.admin.save()

        response = self.get_view(self.admin)

        self.assertEqual(access_view.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
