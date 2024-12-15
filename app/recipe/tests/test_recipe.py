"""
Tests for recipe APIs
"""

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)


RECIPES_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    """ Create and return the url of the specified recipe """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """ Create and return a sample recipe (a helper function to be used in tests) """
    defaults = {
        "title": "Sample recipe",
        "times_in_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample recipe description",
        "link": "https://example.com/sapmle-recipe.pdf",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """ Create and return a new user """
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """ Test for public functionalities of recipe apis """
    
    
    def setUp(self):
        self.client = APIClient()

    
    def test_auth_required(self):
        """ Test authentication is required for the api """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


    
class PrivateRecipeApiTests(TestCase):
    """ Test authenticated api requests """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="password123",
            name="Test Name"
        )
        self.client.force_authenticate(self.user)

    
    def retrieve_recipes(self):
        """ Test retrieving a list of recipes """

        # Create some dummy recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_retrieve_recipes_limited_to_user(self):
        """ Test retrieve recipes list limited to authenticated user """

        other_user = create_user(email="other_user@example.com", password="password123")

        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(other_user)
        create_recipe(other_user)

        res = self.client.get(RECIPES_URL)

        my_recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(my_recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    
    def test_get_recipe_details(self):
        recipe = create_recipe(user=self.user)

        res = self.client.get(recipe_detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        """ Test create a new recipe """

        payload = {
            "title": "Sample recipe",
            "times_in_minutes": 22,
            "price": Decimal("5.25"),
            "description": "Sample recipe description",
            "link": "https://example.com/sapmle-recipe.pdf",
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """ Test partial update of a recipe """

        original_details = {
            "user": self.user,
            "title": "Sample recipe",
            "times_in_minutes": 22,
            "price": Decimal("5.25"),
            "description": "Sample recipe description",
            "link": "https://example.com/sapmle-recipe.pdf",
        }

        recipe = create_recipe(**original_details)

        update = {
            "title": "A wonderful recipe for tomato soup",
            "times_in_minutes": 35
        }

        update_res = self.client.patch(recipe_detail_url(recipe.id), update)
        

        recipe.refresh_from_db()
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, update["title"])
        self.assertEqual(recipe.times_in_minutes, update["times_in_minutes"])
        self.assertEqual(recipe.link, original_details["link"])
        self.assertEqual(recipe.user, self.user)


    def test_full_update(self):
        """Test full update of a recipe"""

        recipe = create_recipe(user=self.user)

        update = {
            # "user": self.user,
            "title": "Sample recipe updated",
            "times_in_minutes": 220,
            "price": Decimal("15.25"),
            "description": "Sample recipe description updated",
            "link": "https://example.com/sapmle-recipe.pdf-updated",
        }

        res= self.client.put(recipe_detail_url(recipe.id), update)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k, v in update.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_user_unable_to_reassign_user(self):
        """Test user can not be updated"""

        recipe = create_recipe(user=self.user)

        other_user = create_user(**{"email":"otheruser@example.com", "password": "password123"})

        # Basically what's happening is that the serializer is dropping the user_id payload because 
        # it's not defined in the serializer. I believe the default behavior of serializers is to 
        # ignore any content in the request which is not defined as a field.
        res = self.client.patch(recipe_detail_url(recipe.id), {"user": other_user})
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        # Following is not working because of the serializer explained above. 
        # Api returns 200 even though user is not updated 
        # self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

    def test_delete_recipe(self):
        """Test delete a recipe"""
        recipe = create_recipe(user=self.user)
        res = self.client.delete(recipe_detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    
    def test_delete_other_user_recipe_gives_error(self):
        """Test deleting a recipe belongs to another user gives an error"""
        other_user = create_user(email="other_user@example.com", password="password123")
        recipe = create_recipe(user=other_user)
        res = self.client.delete(recipe_detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())