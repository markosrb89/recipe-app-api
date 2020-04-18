from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """
    Manage tags in the database.
    ListModelMixin, CreateModelMixin: rest_framework feature
    which allows specific functionality for the ViewSet.
    For this API I don't want update/delete
    functionality hence I use ListModelMixin - GenericView
    and CreateModelMixin combination to just list and create the tags.
    """

    """Requires that token authentication is used"""
    authentication_classes = (TokenAuthentication,)
    """Requires that user is authenticated to use the API"""
    permission_classes = (IsAuthenticated,)
    """
    When GenericViewSet and ListModelMixin are used,
    I need to provide the queryset that I want to return.
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """
        Override get_queryset function to return objects for the current
        authenticated user only.
        When ViewSet is invoked from a url, it will call get_queryset
        to retrieve these objects (queryset = Tag.objects.all()) and here
        I can apply any custom filtering like limiting it to
        the authenticated user, so whatever I return here it
        will be displayed in the API.
        """

        """User is assigned to the request since authentication is required"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Assign a newly created tag to the correct user.
        Similar to the get_queryset function.
        This function allows to hook into the create
        process when creating an object.
        So, when I do create an object in the ViewSet,
        this function will be invoked and the validated serializer
        will be passed in as a serializer argument and then I can
        perform any modifications here that I want to create process.
        Here I just set the user to the authenticated user.
        """
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)
