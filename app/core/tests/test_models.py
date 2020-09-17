from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='usman@gmail.com', password='123456'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test the tag string presentation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string presentation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Salt"
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=10.00,
        )
        self.assertEqual(str(recipe), recipe.title)
