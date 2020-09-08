from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload successfully."""
        payload = {
            'email': 'usman@gmail.com',
            'password': 'testpass',
            'name': 'Usman'
        }
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', result.data)
        user = get_user_model().objects.get(**result.data)
        self.assertTrue(user.check_password(payload['password']))

    def test_user_exists(self):
        """Test creating a user that already exist fails"""
        payload = {'email': 'usman@gmail.com', 'password': 'testpass'}
        create_user(**payload)
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 character."""
        payload = {'email': 'user@gmail.com', 'password': '1234'}
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {'email': 'usman@gmail.com', 'password': '123456'}
        create_user(**payload)
        result = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given."""
        create_user(**{'email': 'usman@gmail.com', 'password': '123456'})
        payload = {'email': 'usman@gmail.com', 'password': 'wrong'}
        result = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not created"""
        payload = {'email': 'user@gmail.com', 'password': '123456'}
        result = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test that authentication is required for users."""
        result = self.client.get(ME_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='usman@gmail.com',
            password='123456',
            name='USMAN'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving user profile for logged in user"""
        result = self.client.get(ME_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allow(self):
        result = self.client.post(ME_URL)
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """"Test updating the user profile for authenticated user"""
        payload = {'name': 'ALI', 'password': '123456'}
        result = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
