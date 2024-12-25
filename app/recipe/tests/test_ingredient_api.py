"""
Test for the ingredient api
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

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
