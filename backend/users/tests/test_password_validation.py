from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from users.models import User


class PasswordValidatorTests(SimpleTestCase):
    def assert_rejected_with(self, password, code, user=None):
        with self.assertRaises(ValidationError) as context:
            validate_password(password, user)

        codes = [error.code for error in context.exception.error_list]
        self.assertIn(code, codes)

    def test_strong_password_is_accepted(self):
        self.assertIsNone(validate_password("Kata-Sandi-Kuat-2026"))

    def test_too_short_password_is_rejected(self):
        self.assert_rejected_with("Ab1-xyz", "password_too_short")

    def test_common_password_is_rejected(self):
        self.assert_rejected_with("password", "password_too_common")

    def test_numeric_only_password_is_rejected(self):
        self.assert_rejected_with("4829105736", "password_entirely_numeric")

    def test_password_similar_to_email_is_rejected(self):
        user = User(email="budi.santoso@example.com", name="Budi Santoso")

        self.assert_rejected_with("budi.santoso", "password_too_similar", user)
