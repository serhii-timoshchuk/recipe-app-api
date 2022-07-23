"""
Tests for ingredients API queries
"""
from decimal import Decimal

from rest_framework.test import APIClient
from rest_framework import status

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return a detail url of particular ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@exqmple.com', password='testpasswod123'):
    """Create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API queries"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requeried(self):
        """Test auth is required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients is successful"""
        Ingredient.objects.create(user=self.user, name='Ingredient 1')
        Ingredient.objects.create(user=self.user, name='Ingredient 2')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""
        user2 = create_user(email='test2user@example.com')
        Ingredient.objects.create(
            user=user2, name="Ingredient for second user"
        )
        new_ingredient = Ingredient.objects.create(
            user=self.user, name='Ingredient 1'
        )
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], new_ingredient.name)
        self.assertEqual(res.data[0]['id'], new_ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient is successful."""
        ingredient = Ingredient.objects.create(user=self.user, name='Test')
        url = detail_url(ingredient.id)
        payload = {'name': 'Garlic'}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient is successful"""
        ingredient = Ingredient.objects.create(
            user=self.user, name="Will be deleted"
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        i1 = Ingredient.objects.create(user=self.user, name='Apple')
        i2 = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = Recipe.objects.create(
            user=self.user,
            title='default title',
            time_minutes=22,
            price=Decimal('5.25'),
            description='some description',
            link='http://example.com/recipe.pdf')

        recipe.ingredients.add(i1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(i1)
        s2 = IngredientSerializer(i2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredients_uniq(self):
        """Test filtered ingredients return a unique list"""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Apples')
        r1 = Recipe.objects.create(
            user=self.user,
            title='Herb eggs',
            time_minutes=22,
            price=Decimal('5.25'),
            description='some description',
            link='http://example.com/recipe.pdf')
        r2 = Recipe.objects.create(
            user=self.user,
            title='Fry Eggs',
            time_minutes=22,
            price=Decimal('5.25'),
            description='some description',
            link='http://example.com/recipe.pdf')
        r1.ingredients.add(ing)
        r2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
