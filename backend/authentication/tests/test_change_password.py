from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"
NEW_PASSWORD = "Kata-Sandi-Baru-2026"


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.url = reverse("password-change")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}",
        )

    def post_change(self, old=PASSWORD, new=NEW_PASSWORD):
        return self.client.post(
            self.url,
            {"old_password": old, "new_password": new},
            format="json",
        )

    def post_login(self, password):
        return self.client.post(
            reverse("login"),
            {"email": "budi@example.com", "password": password},
            format="json",
        )

    def post_refresh(self, token):
        return self.client.post(
            reverse("token-refresh"),
            {"refresh": str(token)},
            format="json",
        )

    def is_blacklisted(self, token):
        return BlacklistedToken.objects.filter(token__jti=token["jti"]).exists()

    def test_change_password_succeeds(self):
        response = self.post_change()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    def test_old_password_stops_working_for_login(self):
        self.post_change()

        response = self.post_login(PASSWORD)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_password_can_log_in_and_refresh(self):
        self.post_change()

        login = self.post_login(NEW_PASSWORD)
        refreshed = self.post_refresh(login.data["refresh"])

        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)

    def test_wrong_old_password_is_rejected(self):
        response = self.post_change(old="salah-banget")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"old_password": ["Wrong password."]})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_weak_new_password_is_rejected(self):
        response = self.post_change(new="12345678")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_new_password_similar_to_email_is_rejected(self):
        response = self.post_change(new="budi@example.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_missing_fields_are_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)
        self.assertIn("new_password", response.data)

    def test_requires_access_token(self):
        self.client.credentials()

        response = self.post_change()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_change_revokes_all_refresh_tokens(self):
        other_device = RefreshToken.for_user(self.user)

        self.post_change()

        self.assertTrue(self.is_blacklisted(self.refresh))
        self.assertTrue(self.is_blacklisted(other_device))
        self.assertEqual(
            self.post_refresh(self.refresh).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.post_refresh(other_device).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_change_keeps_other_users_tokens(self):
        other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )
        others_token = RefreshToken.for_user(other_user)

        self.post_change()

        self.assertFalse(self.is_blacklisted(others_token))
        self.assertEqual(
            self.post_refresh(others_token).status_code, status.HTTP_200_OK
        )

    def test_failed_change_keeps_refresh_tokens(self):
        self.post_change(old="salah-banget")

        self.assertFalse(self.is_blacklisted(self.refresh))
        self.assertEqual(
            self.post_refresh(self.refresh).status_code, status.HTTP_200_OK
        )

    def test_current_access_token_stays_valid_until_it_expires(self):
        self.post_change()

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
