"""
Test for the tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URLS = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='example@example.com', password='testpassword123'):
    """Create and return new user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, name='Test tag'):
    return Tag.objects.create(user=user, name=name)


class PublicTagsApiTest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(TAGS_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags is successful"""
        create_tag(user=self.user, name='Dessert')
        create_tag(user=self.user, name='Vegan')

        res = self.client.get(TAGS_URLS)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""
        user2 = create_user(email='test2@example.com')
        create_tag(user=user2, name='2user tag')
        tag = create_tag(user=self.user, name='Comfort')
        res = self.client.get(TAGS_URLS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating tg is successful"""
        tag = create_tag(user=self.user, name='after dinner')
        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag is successful"""
        tag = create_tag(user=self.user)
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
