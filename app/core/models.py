"""
Database models
"""

from django.conf import settings
from django.db import models 

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """ Manager for users """

    # password is defaulted to None here. This gives flexibility to create
    # unusable users (for testing etc.) 
    def create_user(self, email, password=None, **extra_fields):
        """ Create, save and return a new user """
        if not email:
            raise ValueError("User must have a email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # The name of this function is important. Django cli looks up this name
    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        return user
        

class User(AbstractBaseUser, PermissionsMixin):
    """ Users in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # bind this class with the manager
    objects = UserManager()

    # This replaces the default username field in AbstractBaseUser to email
    USERNAME_FIELD = "email"


class Recipe(models.Model):
    """ Recipe object """
    user = models.ForeignKey(
        # We could use here directly a string here. However it is best practice 
        # to make it dynamic so that we do not need to change code here if we 
        # need to change user model 
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    times_in_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')


    def __str__(self):
        return self.title
    

class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
