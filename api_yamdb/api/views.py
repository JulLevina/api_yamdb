# from django.shortcuts import get_object_or_404
from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.mixins import CreateModelMixin, ListModelMixin
# from rest_framework.pagination import LimitOffsetPagination
# from rest_framework.filters import SearchFilter

from v1.models import Title, Categories, Genres
from .serializers import TitleSerializer, CategoriesSerializer
from .serializers import GenresSerializer
# from .permissions import IsOwnerOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
