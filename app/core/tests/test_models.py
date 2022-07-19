"""
Test for models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(email='test@example.com', password='testPas123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTEst(TestCase):
    """Test models"""

    def test_create_user_with_email(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'UserfTeds123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is nirmalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test3@example.COM', 'test3@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating user without an email raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '1123sample')

    def test_create_super_user(self):
        """Test creting a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'sample123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            'test@examle.com',
            'testpaswords'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe",
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()

        tag = models.Tag.objects.create(
            user=user,
            name='Test tag'
        )
        self.assertEqual(str(tag), tag.name)
