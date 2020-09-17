from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe."""
    default = {
        'title':'sample recipe',
        'price':5.00,
        'time_minutes':10
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API test"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        result = self.client.get(RECIPES_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API test"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='usman@gmail.com',
            password='123456'
        )
        self.client.force_authenticate(self.user)

    def test_retrieves_recipe(self):
        """Test retrieving a list of serializer"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        result = self.client.get(RECIPES_URL)
        
        recipe = Recipe.objects.all()
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test retrieving recipes for user"""
        user1 = get_user_model().objects.create_user(
            email='usman1@gmail.com',
            password='123456'
        )
        sample_recipe(user1)
        sample_recipe(self.user)

        result = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        result = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'price': 5.00,
            'time_minutes': 10
        }
        result = self.client.post(RECIPES_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        
        recipe = Recipe.objects.get(id=result.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'price': 5.00,
            'time_minutes': 10
        }
        result = self.client.post(RECIPES_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=result.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredient"""
        ingredient1 = sample_ingredient(user=self.user, name='Genger')
        ingredient2 = sample_ingredient(user=self.user, name='LadyFinger')
        payload = {
            'title': 'Thai',
            'ingredients': [ingredient1.id, ingredient2.id],
            'price': 5.00,
            'time_minutes': 10,
        }
        result = self.client.post(RECIPES_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=result.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {'title': 'chicken tikha', 'tags':[new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        
        self.assertEqual(recipe.title, payload['title'])
        
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {'title': 'Biryani', 'price': 10, 'time_minutes': 25}
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
        



















    
    








