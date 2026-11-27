from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"


class RefreshTests(APITestCase):
    def setUp(self):
        self.url = reverse("token-refresh")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.refresh = RefreshToken.for_user(self.user)

    def post_refresh(self, token):
        return self.client.post(self.url, {"refresh": str(token)}, format="json")

    def test_valid_refresh_token_returns_new_access_token(self):
        response = self.post_refresh(self.refresh)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = AccessToken(response.data["access"])
        self.assertEqual(access["user_id"], str(self.user.pk))

    def test_refresh_token_is_not_rotated_yet(self):
        # Rotasi refresh token ditinjau di T4.2; kalau diaktifkan, ubah tes ini.
        response = self.post_refresh(self.refresh)

        self.assertEqual(set(response.data), {"access"})

    def test_garbage_token_is_rejected(self):
        response = self.post_refresh("bukan-token-asli")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "token_not_valid")

    def test_access_token_cannot_be_used_as_refresh(self):
        response = self.post_refresh(self.refresh.access_token)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "token_not_valid")

    def test_blacklisted_token_is_rejected(self):
        self.refresh.blacklist()

        response = self.post_refresh(self.refresh)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("blacklisted", str(response.data["detail"]))

    def test_expired_token_is_rejected(self):
        expired = RefreshToken.for_user(self.user)
        expired.set_exp(lifetime=-timedelta(seconds=1))

        response = self.post_refresh(expired)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "token_not_valid")

    def test_missing_refresh_field_is_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)
