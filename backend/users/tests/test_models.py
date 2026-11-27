from django.db import IntegrityError, transaction
from django.test import TestCase

from users.models import User

PASSWORD = "Kata-Sandi-Kuat-2026"


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )

        self.assertEqual(user.email, "budi@example.com")
        self.assertEqual(user.name, "Budi")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(User.objects.count(), 1)

    def test_password_is_stored_as_hash(self):
        user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )

        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.check_password("salah"))

    def test_email_must_be_unique(self):
        User.objects.create_user(
            email="sama@example.com",
            password=PASSWORD,
            name="Pertama",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                email="sama@example.com",
                password=PASSWORD,
                name="Kedua",
            )

    def test_role_defaults_to_user(self):
        user = User.objects.create_user(
            email="budi@example.com",
            password=PASSWORD,
            name="Budi",
        )

        self.assertEqual(user.role, User.Role.USER)
