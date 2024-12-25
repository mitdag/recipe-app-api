"""
Views for user api.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system """

    serializer_class = UserSerializer


class CreateAuthTokenView(ObtainAuthToken):
    """ Create a new token for the user """
    serializer_class = AuthTokenSerializer
    # This optional. It makes the browseable api nicer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user """
    serializer_class = UserSerializer
    # We specify which auth mechanism wer are using. We use token in
    # this project (not jwt token)
    authentication_classes = [authentication.TokenAuthentication]
    # Only authenticated user can use this api
    permission_classes = [permissions.IsAuthenticated]

    # When user authenticates user is attached to the request by
    # rest_framework. We override get_object method to return the user.
    # When a http.get request is made to this api this method is
    # get called to get the authenticated user and then it is
    # run through the serializer that we defined before the result is
    # returned to the api
    def get_object(self):
        # Retrieve and return the current user
        return self.request.user
