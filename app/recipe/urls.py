"""
URL mappings for recipe app
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
# This will create an endpoint api/recipes and will assign 
# all possible methods (get, post, put, patch, delete) to the viewset
# That is, all possible urls are created by the router automatically
router.register("recipes",  views.RecipeViewSet)

router.register('tags', views.TagViewSet)
router.register("ingredients", views.IngredientsViewSet)

app_name = "recipe"

urlpatterns = [
    path("", include(router.urls)),
]
