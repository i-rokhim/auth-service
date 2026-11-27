from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"
REJECTED = ["Token tidak valid atau sudah dicabut."]


class LogoutTests(APITestCase):
    def setUp(self):
        self.url = reverse("logout")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

    def post_logout(self, token):
        return self.client.post(self.url, {"refresh": str(token)}, format="json")

    def is_blacklisted(self, token):
        return BlacklistedToken.objects.filter(token__jti=token["jti"]).exists()

    def test_logout_blacklists_refresh_token(self):
        response = self.post_logout(self.refresh)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertTrue(self.is_blacklisted(self.refresh))

    def test_revoked_token_cannot_be_refreshed(self):
        self.post_logout(self.refresh)

        response = self.client.post(
            reverse("token-refresh"),
            {"refresh": str(self.refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_revokes_only_the_given_token(self):
        other_device = RefreshToken.for_user(self.user)

        self.post_logout(self.refresh)
        response = self.client.post(
            reverse("token-refresh"),
            {"refresh": str(other_device)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.is_blacklisted(other_device))

    def test_logout_requires_access_token(self):
        self.client.credentials()

        response = self.post_logout(self.refresh)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self.is_blacklisted(self.refresh))

    def test_invalid_access_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer bukan-token-asli")

        response = self.post_logout(self.refresh)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_garbage_refresh_token_is_rejected(self):
        response = self.post_logout("bukan-token-asli")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"refresh": REJECTED})

    def test_access_token_cannot_be_used_as_refresh(self):
        response = self.post_logout(self.refresh.access_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"refresh": REJECTED})

    def test_other_users_refresh_token_is_rejected(self):
        others_token = RefreshToken.for_user(self.other_user)

        response = self.post_logout(others_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"refresh": REJECTED})
        self.assertFalse(self.is_blacklisted(others_token))

    def test_second_logout_with_same_token_is_rejected(self):
        first = self.post_logout(self.refresh)
        second = self.post_logout(self.refresh)

        self.assertEqual(first.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second.data, {"refresh": REJECTED})

    def test_missing_refresh_field_is_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)
