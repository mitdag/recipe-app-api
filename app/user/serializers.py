"""
Serializers for the user API View
"""

from django.contrib.auth import (
    get_user_model,
    authenticate # this is used for token serialization
)
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the User object """

    class Meta:
        model = get_user_model()
        # We want from the user only following fields. is_staff etc is not
        # a concern of the user. Admins must set them
        fields = ["email", "password", "name"]

        # We want user to write the password but not return it back in the
        # response. Thus we make password field as write_only
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


    def create(self, validated_data):
        """Create and return a user with encrypted password """
        return get_user_model().objects.create_user(**validated_data)   
    

    def update(self, instance, validate_data):
        """ Update and return user """

        # We make the password update optional for the user. If he specifies one 
        # we update it, do not touch the current password otherwise
        password = validate_data.pop("password", None)

        user = super().update(instance, validate_data)

        if password:
            user.set_password(password)
            user.save()
        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        # When we are using browseable api we want the password to be hidden
        style={"input_type": "password"},
        # Django rest_framework's default behavior is to trim whitespace from char inputs 
        # we do not want it, because user can be able to add whitespaces in his password
        trim_whitespace=False,
    )

    
    def validate(self, attrs):
        """ Validate and authenticate the user """
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            msg = _("Unable to authenticate with the provided credentials")
            raise serializers.ValidationError(msg, code="authorization")
        
        attrs["user"] = user
        return attrs