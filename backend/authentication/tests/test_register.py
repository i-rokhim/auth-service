from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

PASSWORD = 'Kata-Sandi-Kuat-2026'


class RegisterTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.payload = {
            'email': 'budi@example.com',
            'name': 'Budi',
            'password': PASSWORD,
        }

    def test_register_creates_user(self):
        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data), {'id', 'email', 'name', 'role'})
        self.assertEqual(response.data['email'], 'budi@example.com')
        self.assertEqual(response.data['role'], 'user')
        user = User.objects.get(email='budi@example.com')
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_response_never_contains_password(self):
        response = self.client.post(self.url, self.payload, format='json')

        self.assertNotIn('password', response.data)
        self.assertNotIn(PASSWORD, str(response.content))

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email='budi@example.com',
            password=PASSWORD,
            name='Pertama',
        )

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(User.objects.filter(email='budi@example.com').count(), 1)

    def test_weak_password_is_rejected(self):
        self.payload['password'] = 'password'

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(email='budi@example.com').exists())

    def test_invalid_email_is_rejected(self):
        self.payload['email'] = 'bukan-email'

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_missing_fields_are_reported_per_field(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {'email', 'name', 'password'})

    def test_role_and_staff_flags_cannot_be_set_by_client(self):
        self.payload.update({'role': 'admin', 'is_staff': True, 'is_superuser': True})

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='budi@example.com')
        self.assertEqual(user.role, User.Role.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)