"""
URL mappings for the user api
"""

from django.urls import path

from user import views

# This app name will be used in reverse function
# (e.g CREATE_USER_URL = reverse("user:create") in tests/test_user_api.py)
app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("token/", view=views.CreateAuthTokenView.as_view(), name="token"),
    path("me/", view=views.ManageUserView.as_view(), name="me")
]
