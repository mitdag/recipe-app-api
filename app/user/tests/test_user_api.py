"""
Tests for the user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """ Create and return a new user """
    return get_user_model().objects.create_user(**params)


# We create 2 test classes:
#   1. Public tests: unauthenticated tests (e.g. user registration)
#   2. Private tests: authenticated tests
class PublicUserApiTests(TestCase):
    """ Test the public features of the user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """ Test creating a user is successful """
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        # check that user's password is not accidentally put in the response
        self.assertNotIn("password", res.data)

    def test_user_with_email_exist_error(self):
        """ Test error returned if user with email exists """

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returns if the password is shorter
        than 5 chars """

        payload = {
            "email": "test@example.com",
            "password": "pass",
            "name": "Test User"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """ Test creates token for valid credentials """

        user_details = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }

        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"]
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """ Test a token is not created for invalid credentials """

        create_user(email="test@example.com", password="good_pass")

        payload = {
            "email": "test@example.com",
            "password": "bad_pass"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """ Test posting a blank password returns error """
        payload = {
            "email": "test@example.com",
            "password": ""
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test authentication is required for users """

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Test the private features of the user api """

    def setUp(self):
        self.client = APIClient()
        user_details = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test Name"
        }
        self.user = create_user(**user_details)

        # We are not testing if the token mechanism is working. Thus we do
        # not create a token by calling token api. Instead we want
        # rest_framework do this for us. Any request that we make to apis
        # by using this user from here on will be authenticated
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test profile for logged in user """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "email": self.user.email,
            "name": self.user.name,
        })

    def test_post_me_not_allowed(self):
        """ Test post method is not allowed for me api.We use
        patch for updating. """

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test user can update his profile """

        payload = {
            "name": "updated_name",
            "password": "updated_new_password123"
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.data.get("name"), payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
