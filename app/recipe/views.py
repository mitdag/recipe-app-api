"""
Views for recipe APIs
"""

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins,
    status
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response


from core.models import (
    Ingredient,
    Recipe,
    Tag,
)
from recipe import serializers


# This decorator is used for query parameter configuration
# It allows us to extend auto generated schemas by drf-spectacular
# Query param schemas are not generated automatically, thus we add them here.
@extend_schema_view(
    # This means we want to extend schema for list endpoint
    list=extend_schema(
        parameters=[
            # Specifies the details of the parameter
            OpenApiParameter(
                # name of the param
                'tags',
                # type of the param is string (we are expecting a string which
                # contains list of ids separated by commas )
                OpenApiTypes.STR,
                # For documentation
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
# ModelViewSet is very convenient for directly working with models
class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer

    # The queryset variable in your RecipeViewSet class represents the
    # default list of objects that this viewset will work with.
    # It defines the data source for the operations performed by the
    # RecipeViewSet.
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # This is a helper function to convert query params to ints
    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # query parameters are id numbers that are placed in a string and
        # separated  with commas exp: '4,2,5'
        return [int(str_id) for str_id in qs.split(',')]

    # Without this method overridden default queryset will return everything
    # With this method we customize how it behaves
    def get_queryset(self):
        # This was the original implementation of the method which does not
        # take the query params into account.
        # return self.queryset.filter(user=self.request.user).order_by("-id")

        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        # We use distinct here because we could get duplicate results if an
        # ingredient or tag assigned to the recipe
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    # We override this method the switch between serializers
    # (RecipeSerializer or RecipeDetailSerializer) according to the request.
    # If the request is a listing then we return RecipeSerializer
    # (an overview of the recipe). For other request (detail,
    # update etc) we return RecipeDetailSerializer
    def get_serializer_class(self):
        """Return appropriate serializer according to the request """

        if self.action == "list":
            return serializers.RecipeSerializer
        # View has some default actions, such as list, delete, update
        # We can also add custom actions on top of this.
        # upload_image is a custom action defined upload_image function below
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # We override this method to save the created recipe into the db.
    # Since user who creates the recipe is not part of the serializer
    # we need to set it here.(user is a foreign key in recipe)

    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(user=self.request.user)

    # detail=True means that this action applies to post requests for a
    # specific recipe (applies to detail endpoints)
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""

        # get_object() will get the recipe by using pk provided in the
        # parameter list
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
# Order in the inheritance is important here: First mixin than GenericViewSet
class BaseRecipeAttrViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(BaseRecipeAttrViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
