from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from users.models import User

EMAIL = 'budi@example.com'
PASSWORD = 'Kata-Sandi-Kuat-2026'


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            name='Budi',
        )

    def login(self, email=EMAIL, password=PASSWORD):
        return self.client.post(
            self.url,
            {'email': email, 'password': password},
            format='json',
        )

    def test_login_returns_tokens_and_user(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {'refresh', 'access', 'user'})
        self.assertEqual(
            dict(response.data['user']),
            {'id': self.user.pk, 'email': EMAIL, 'name': 'Budi', 'role': 'user'},
        )

    def test_response_never_contains_password(self):
        response = self.login()

        self.assertNotIn('password', response.data['user'])
        self.assertNotIn(PASSWORD, str(response.content))

    def test_token_lifetimes_match_settings(self):
        response = self.login()

        access = AccessToken(response.data['access'])
        refresh = RefreshToken(response.data['refresh'])
        self.assertEqual(access['user_id'], str(self.user.pk))
        self.assertEqual(access['exp'] - access['iat'], 15 * 60)
        self.assertEqual(refresh['exp'] - refresh['iat'], 7 * 24 * 60 * 60)

    def test_wrong_password_and_unknown_email_look_the_same(self):
        wrong_password = self.login(password='salah-banget')
        unknown_email = self.login(email='tidak-ada@example.com')

        self.assertEqual(wrong_password.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown_email.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(wrong_password.data, unknown_email.data)
        self.assertNotIn('access', wrong_password.data)

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save()

        response = self.login()
        wrong_password = self.login(password='salah-banget')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, wrong_password.data)

    def test_missing_fields_are_reported_per_field(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {'email', 'password'})