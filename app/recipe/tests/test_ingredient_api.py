from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    """Test the publicaly available ingredient api"""
    def setUp(self):
        self.client = APIClient()

    def test(self):
        result = self.client.get(INGREDIENT_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test the private ingredient api"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='usman@gmail.com',
            password='123456'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='salt')
        Ingredient.objects.create(user=self.user, name='Kale')

        result = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""
        user1 = get_user_model().objects.create(
            email='usman1@gmail.com',
            password='123456'
        )
        Ingredient.objects.create(user=user1, name='kale')
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')

        result = self.client.get(INGREDIENT_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'Salt'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        result = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Meat')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Chelli')
        recipe = Recipe.objects.create(
            title='Biryani',
            time_minutes=15,
            price=50,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        
        result = self.client.get(INGREDIENT_URL, {'assigned_only':1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, result.data)
        self.assertNotIn(serializer2.data, result.data)
