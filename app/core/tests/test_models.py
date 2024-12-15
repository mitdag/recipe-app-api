"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

# We do not need to import User model, since we use build in get_user_model
# However we need to import other models.
from core import models

def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """ Test models """

    def test_create_user_with_email_successful(self):
        """ Test creating user with email is successful """

        # @test.com is a reserved domain for tests. 
        # Django does not send emails to this domain
        email = "test@example.com"
        password = "password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """ Test the email is normalized when a new user is created"""

        emails = [
            ["test1@test.com", "test1@test.com"],
            ["test2@TEST.com", "test2@test.com"],
            ["test3@test.COM", "test3@test.com"],
            ["Test4@Test.coM", "Test4@test.com"],
        ]

        for email, expected in emails:
            user = get_user_model().objects.create_user(email=email, password="password")

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(expected_exception=ValueError):
            get_user_model().objects.create_user(email="", password="password")
    

    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser(
            email="superuser@test.com",
            password="password"
        )

        self.assertEqual(user.email, "superuser@test.com")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    
    def test_create_recipe(self):
        """ Test creating a recipe is successful """

        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password123"
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            times_in_minutes=5,
            # Default is float. Since Decimal is more accurate we use it here.
            price=Decimal("5.50"),
            description="Sample recipe description"
        )

        self.assertEqual(str(recipe), recipe.title)

    
    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)    

    
        