"""
Serializers for recipe apis
"""

from rest_framework import serializers

from core.models import (
    Ingredient,
    Recipe,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients"""

    class Meta:
        model = Ingredient
        fields = ["name", "id"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipe """
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "times_in_minutes",
                  "price", "link", "tags", "ingredients"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed"""
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(
                user=auth_user, **ingredient)
            recipe.ingredients.add(ing_obj)

    # By default nested serializers are readonly. To make them writable
    # we need to override and customize create method for post methods
    def create(self, validated_data):
        """Create a recipe."""
        # We remove the tags from validated_data first
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        # Now we can use validated_data to create recipe (without tags and
        # ingredients)
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags=tags, recipe=recipe)
        self._get_or_create_ingredients(ingredients=ingredients, recipe=recipe)

        return recipe

    # By default nested serializers are readonly. To make them writable
    # we need to override and customize update method for put and patch methods
    def update(self, instance, validated_data):
        """Update recipe."""

        # We want to process also empty tags list (for clear), thus we assign
        # the default value to None (not [] as in create method)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(
                ingredients=ingredients, recipe=instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for recipe details view """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}
