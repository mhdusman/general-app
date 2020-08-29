from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with email successful"""
        email = 'usman@gmail.com'
        password = '123456'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'usman@GMAIL.coM'
        user = get_user_model().objects.create_user(email, 'dsf333')
        self.assertEqual(user.email, email.lower())

    def test_user_with_invalid_email(self):
        """Test create new user with no email raise error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'fdsfds')

    def test_create_new_superuser(self):
        """Test create new superuser"""
        user = get_user_model().objects.create_superuser(
            'usman@gmail.com', '123456')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
