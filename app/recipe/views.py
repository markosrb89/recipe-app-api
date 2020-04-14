from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Manage tags in the database.
    ListModelMixin: rest_framework feature.
    For this API I don't want update/create/delete
    functionality hence I use ListModelMixin - GenericView
    combination to just list the tags.
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
