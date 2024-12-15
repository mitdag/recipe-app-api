"""
Tests for admin modifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """ Tests for Django admin """

    # This method name is important
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password"
        )

        self.test_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password",
            name="Test User",
        )

        self.client.force_login(self.admin)

    def test_users_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.test_user.email)
        self.assertContains(res, self.test_user.name)

    def test_edit_user_page(self):
        url = reverse("admin:core_user_change", args=[self.test_user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse("admin:core_user_add")

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)