from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"


class ProfileTests(APITestCase):
    def setUp(self):
        self.url = reverse("profile")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.authenticate(self.user)

    def authenticate(self, user):
        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def patch_profile(self, data):
        return self.client.patch(self.url, data, format="json")

    def test_get_returns_own_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self.user.pk,
                "email": "budi@example.com",
                "name": "Budi",
                "role": "user",
            },
        )

    def test_get_never_includes_password(self):
        response = self.client.get(self.url)

        self.assertNotIn("password", response.data)

    def test_get_returns_only_the_token_owners_profile(self):
        other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )
        self.authenticate(other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.data["email"], "ani@example.com")

    def test_get_requires_access_token(self):
        self.client.credentials()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_access_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer bukan-token-asli")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_updates_name(self):
        response = self.patch_profile({"name": "Budi Baru"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Budi Baru")
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Budi Baru")

    def test_patch_response_has_same_shape_as_get(self):
        get_response = self.client.get(self.url)

        patch_response = self.patch_profile({"name": "Budi Baru"})

        self.assertEqual(set(patch_response.data), set(get_response.data))

    def test_patch_ignores_role(self):
        response = self.patch_profile({"name": "Budi Baru", "role": "admin"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "user")
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.USER)

    def test_patch_ignores_email(self):
        response = self.patch_profile(
            {"name": "Budi Baru", "email": "penyusup@example.com"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "budi@example.com")

    def test_patch_blank_name_is_rejected(self):
        response = self.patch_profile({"name": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"name": ["This field may not be blank."]})
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Budi")

    def test_patch_too_long_name_is_rejected(self):
        response = self.patch_profile({"name": "x" * 151})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_patch_requires_access_token(self):
        self.client.credentials()

        response = self.patch_profile({"name": "Budi Baru"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Budi")

    def test_patch_does_not_touch_other_users(self):
        other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )

        self.patch_profile({"name": "Budi Baru"})

        other_user.refresh_from_db()
        self.assertEqual(other_user.name, "Ani")

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url, {"name": "Budi Baru"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
