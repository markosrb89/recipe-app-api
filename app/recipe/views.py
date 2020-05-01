from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """
    Base viewset for user owned recipe attributes
    ListModelMixin, CreateModelMixin: rest_framework feature
    which allows specific functionality for the ViewSet.
    For this API I don't want update/delete
    functionality hence I use ListModelMixin - GenericView
    and CreateModelMixin combination to just list and
    create the tags/ingredients.
    """

    """Requires that token authentication is used"""
    authentication_classes = (TokenAuthentication,)
    """Requires that user is authenticated to use the API"""
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Override get_queryset function to return objects for the current
        authenticated user only.
        When ViewSet is invoked from a url, it will call get_queryset
        to retrieve these objects (queryset = Tag.objects.all() ||
        Ingredient.objects.all()) and here
        I can apply any custom filtering like limiting it to
        the authenticated user, so whatever I return here it
        will be displayed in the API.
        """

        """User is assigned to the request since authentication is required"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Assign a newly created tag/ingredient to the correct user.
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


class TagViewSet(BaseRecipeAttrViewSet):
    """
    Manage tags in the database.
    When GenericViewSet and ListModelMixin are used,
    I need to provide the queryset that I want to return.
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer class based
        on the actions in the viewset.
        Here I have two actions: list and retrieve
        """
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Enable creating a new recipe.
        Assign the user of the recipe to the current
        authenticated user.
        """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
