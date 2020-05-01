import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                       PermissionsMixin
from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    extension = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{extension}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        """Creates a new user model"""
        user = self.model(email=self.normalize_email(email), **extra_fields)
        """Save password encrypted"""
        user.set_password(password)
        """Save the user by supporting multiple databases"""
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user modal that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    """
    User foreign key. Instead of referencing User model
    directly, here is used the best practice method of
    retrieving the auth User model setting from main Django
    settings file.
    -> models.ForeignKey(
        MODEL_THAT_FOREIGN_KEY_IS_BASED_OFF,
        WHAT_HAPPENS_WHITH_THE_TAG_WHEN_USER_IS_DELETED
    )
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # String representation of the model
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
