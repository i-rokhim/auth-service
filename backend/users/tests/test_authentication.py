from django.contrib.auth import authenticate
from django.test import TestCase

from users.models import User

EMAIL = 'budi@example.com'
PASSWORD = 'Kata-Sandi-Kuat-2026'


class AuthenticateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            name='Budi',
        )

    def test_correct_email_and_password_is_accepted(self):
        user = authenticate(email=EMAIL, password=PASSWORD)

        self.assertEqual(user, self.user)

    def test_wrong_password_is_rejected(self):
        user = authenticate(email=EMAIL, password='salah')

        self.assertIsNone(user)

    def test_unknown_email_is_rejected(self):
        user = authenticate(
            email='tidak-ada@example.com',
            password=PASSWORD,
        )

        self.assertIsNone(user)

    def test_inactive_account_is_rejected(self):
        self.user.is_active = False
        self.user.save()

        user = authenticate(email=EMAIL, password=PASSWORD)

        self.assertIsNone(user)