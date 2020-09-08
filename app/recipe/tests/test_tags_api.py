from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        result = self.client.get(TAGS_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='usman@gmail.com',
            password='123456'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """Test retrieving data"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Butter')
        result = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user1 = get_user_model().objects.create(
            email='usman1@gmail.com',
            password='123456'
        )
        Tag.objects.create(user=user1, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Butter')
        result = self.client.get(TAGS_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]['name'], tag.name)

    def test_create_tag_successfully(self):
        """Test creating a new tag"""
        payload = {'name': 'Vegan'}
        self.client.post(TAGS_URL, payload)
        exist = Tag.objects.filter(
            name=payload['name'],
            user=self.user
        )
        self.assertTrue(exist)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        result = self.client.post(TAGS_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
