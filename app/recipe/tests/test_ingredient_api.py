"""
Test for the ingredient api
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Ingredient,
    Recipe
)

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")

def create_user(email="test@example.com", password="password123"):
    return get_user_model().objects.create_user(email=email, password=password) # type: ignore

def create_ingredient(user, name="Test Ingredient"):
    return Ingredient.objects.create(name=name, user=user)

def ingredient_details_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])

class PublicIngredientApiTests(TestCase):
    """Test for public functionalities of ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        """Test unauthenticated cannot retrieve ingredients"""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateIngredientApiTests(TestCase):
    """Tests for private functionalities of ingredients api"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_ingredient_success(self):
        """Test user can get the ingredients"""

        create_ingredient(name="Vanilla", user=self.user)
        create_ingredient(name="Sugar", user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_user_can_not_get_other_users_ingredients(self):
        """Test user can get only own ingredients but not the other user's"""

        other_user = create_user(email="other_user@example.com")
        create_ingredient(name="Salt", user=other_user)

        my_ing = create_ingredient(name="Vanilla", user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], my_ing.id)
        self.assertEqual(res.data[0]["name"], my_ing.name)

    def test_update_success(self):

        ingredient = create_ingredient(name="Vanilla", user=self.user)
        payload = {
            "name":"Salt",
            "user": self.user
        }

        res = self.client.put(ingredient_details_url(ingredient.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, payload["user"])

    def test_delete_success(self):
        """Test delete an ingredient successful"""
        ingredient = create_ingredient(user=self.user)

        res = self.client.delete(ingredient_details_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
        
    def test_create_ingredient(self):
        # We test this functionality in recipe tests because this is the normal use of the 
        # system: when users create a new recipe they create new ingredients or use existing ones.
        pass

# ===================================== TEST FILTERING (QUERY PARAMS) ====================================

    # We test here that only those ingredients which are assigned to a recipe
    # is returned from the endpoint
    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients to those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            times_in_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)
        # 1 in {'assigned_only': 1} means true 
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        # We expect to get only those ingredients that are assigned to a recipe. Thus 
        # ingredient 2 must not be in the response
        self.assertNotIn(s2.data, res.data)

    # We test here that the returning list includes only distinct values
    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            times_in_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            times_in_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
