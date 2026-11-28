import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"
NEW_PASSWORD = "Kata-Sandi-Baru-2026"
GENERIC_MESSAGE = "If the email is registered, a reset link has been sent."
LINK_ERROR = "Invalid or expired reset link."
SUCCESS_MESSAGE = "Password has been reset."


def make_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def link_from_email(message):
    match = re.search(r"uid=([^&\s]+)&token=(\S+)", message.body)
    return match.group(1), match.group(2)


class PasswordResetRequestTests(APITestCase):
    def setUp(self):
        self.url = reverse("password-reset-request")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )

    def post_request(self, email):
        return self.client.post(self.url, {"email": email}, format="json")

    def test_registered_email_gets_generic_response(self):
        response = self.post_request("budi@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": GENERIC_MESSAGE})

    def test_registered_email_receives_one_email(self):
        self.post_request("budi@example.com")

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["budi@example.com"])
        self.assertEqual(message.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(message.subject, "Atur ulang password Auth Service")
        self.assertIn("Budi", message.body)

    def test_email_contains_working_reset_link(self):
        self.post_request("budi@example.com")

        message = mail.outbox[0]
        uid, token = link_from_email(message)
        self.assertIn(f"{settings.FRONTEND_URL}/reset-password.html?uid=", message.body)
        self.assertEqual(force_str(urlsafe_base64_decode(uid)), str(self.user.pk))
        self.assertTrue(default_token_generator.check_token(self.user, token))

    def test_unregistered_email_gets_same_response_and_no_email(self):
        registered = self.post_request("budi@example.com")
        mail.outbox.clear()

        unknown = self.post_request("tidakada@example.com")

        self.assertEqual(unknown.status_code, registered.status_code)
        self.assertEqual(unknown.data, registered.data)
        self.assertEqual(mail.outbox, [])

    def test_email_matching_ignores_case(self):
        response = self.post_request("BUDI@Example.COM")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["budi@example.com"])

    def test_inactive_user_gets_no_email(self):
        self.user.is_active = False
        self.user.save()

        response = self.post_request("budi@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": GENERIC_MESSAGE})
        self.assertEqual(mail.outbox, [])

    def test_blank_email_is_rejected(self):
        response = self.post_request("")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email": ["This field may not be blank."]})
        self.assertEqual(mail.outbox, [])

    def test_invalid_email_format_is_rejected(self):
        response = self.post_request("bukan-email")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email": ["Enter a valid email address."]})
        self.assertEqual(mail.outbox, [])

    def test_missing_email_is_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email": ["This field is required."]})

    def test_request_needs_no_login(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer bukan-token-asli")

        response = self.post_request("budi@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetConfirmTests(APITestCase):
    def setUp(self):
        self.url = reverse("password-reset-confirm")
        self.user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )
        self.uid, self.token = make_link(self.user)

    def post_confirm(self, uid=None, token=None, password=NEW_PASSWORD):
        data = {
            "uid": self.uid if uid is None else uid,
            "token": self.token if token is None else token,
            "new_password": password,
        }
        return self.client.post(self.url, data, format="json")

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

    def assert_link_rejected(self, response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": LINK_ERROR})

    def assert_password_unchanged(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_valid_link_resets_password(self):
        response = self.post_confirm()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": SUCCESS_MESSAGE})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    def test_new_password_can_log_in(self):
        self.post_confirm()

        response = self.post_login(NEW_PASSWORD)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_old_password_stops_working_for_login(self):
        self.post_confirm()

        response = self.post_login(PASSWORD)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_token_is_rejected(self):
        response = self.post_confirm(token="salah-token")

        self.assert_link_rejected(response)
        self.assert_password_unchanged()

    def test_garbage_uid_is_rejected(self):
        response = self.post_confirm(uid="xxx")

        self.assert_link_rejected(response)
        self.assert_password_unchanged()

    def test_unknown_user_uid_is_rejected(self):
        unknown_uid = urlsafe_base64_encode(force_bytes(self.user.pk + 1000))

        response = self.post_confirm(uid=unknown_uid)

        self.assert_link_rejected(response)
        self.assert_password_unchanged()

    def test_inactive_user_link_is_rejected(self):
        self.user.is_active = False
        self.user.save()

        response = self.post_confirm()

        self.assert_link_rejected(response)

    def test_link_of_another_user_is_rejected(self):
        other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )
        other_uid, _ = make_link(other_user)

        response = self.post_confirm(uid=other_uid)

        self.assert_link_rejected(response)
        self.assert_password_unchanged()
        other_user.refresh_from_db()
        self.assertTrue(other_user.check_password(PASSWORD))

    def test_same_link_cannot_be_used_twice(self):
        first = self.post_confirm()
        second = self.post_confirm(password="Kata-Sandi-Lain-2026")

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assert_link_rejected(second)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))

    def test_expired_link_is_rejected(self):
        with override_settings(PASSWORD_RESET_TIMEOUT=-1):
            response = self.post_confirm()

        self.assert_link_rejected(response)
        self.assert_password_unchanged()

    def test_link_lifetime_is_one_hour(self):
        self.assertEqual(settings.PASSWORD_RESET_TIMEOUT, 3600)

    def test_weak_password_is_rejected_and_link_stays_valid(self):
        weak = self.post_confirm(password="12345678")

        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", weak.data)
        self.assert_password_unchanged()
        retry = self.post_confirm()
        self.assertEqual(retry.status_code, status.HTTP_200_OK)

    def test_link_is_checked_before_password_strength(self):
        response = self.post_confirm(token="salah-token", password="12345678")

        self.assert_link_rejected(response)

    def test_missing_fields_are_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"uid", "token", "new_password"})

    def test_reset_revokes_all_refresh_tokens(self):
        first_device = RefreshToken.for_user(self.user)
        second_device = RefreshToken.for_user(self.user)

        self.post_confirm()

        self.assertTrue(self.is_blacklisted(first_device))
        self.assertTrue(self.is_blacklisted(second_device))
        self.assertEqual(
            self.post_refresh(first_device).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.post_refresh(second_device).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_reset_keeps_other_users_tokens(self):
        other_user = User.objects.create_user(
            email="ani@example.com",
            password=PASSWORD,
            name="Ani",
        )
        others_token = RefreshToken.for_user(other_user)

        self.post_confirm()

        self.assertFalse(self.is_blacklisted(others_token))
        self.assertEqual(
            self.post_refresh(others_token).status_code, status.HTTP_200_OK
        )

    def test_reset_needs_no_login(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer bukan-token-asli")

        response = self.post_confirm()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_link_from_email_resets_password(self):
        self.client.post(
            reverse("password-reset-request"),
            {"email": "budi@example.com"},
            format="json",
        )
        uid, token = link_from_email(mail.outbox[0])

        response = self.post_confirm(uid=uid, token=token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
