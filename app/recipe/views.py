"""
Views for recipe APIs
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
)
from recipe import serializers


# ModelViewSet is very convenient for directly working with models
class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer

    # The queryset variable in your RecipeViewSet class represents the 
    # default list of objects that this viewset will work with. 
    # It defines the data source for the operations performed by the RecipeViewSet.
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Without this method overridden default queryset will return everything
    # With this method we customize how it behaves
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")
    
    # We override this method the switch between serializers (RecipeSerializer or
    # RecipeDetailSerializer) according to the request. If the request is a listing
    # then we return RecipeSerializer (an overview of the recipe). For other request (detail,
    # update etc) we return RecipeDetailSerializer
    def get_serializer_class(self):
        """Return appropriate serializer according to the request """

        if self.action == "list":
            return serializers.RecipeSerializer
        
        return self.serializer_class
    

    # We override this method to save the created recipe into the db.
    # Since user who creates the recipe is not part of the serializer
    # we need to set it here.
    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
