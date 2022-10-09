from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from v1.models import Title, Category, Genre
from .serializers import TitleSerializer, CategoriesSerializer
from .serializers import GenresSerializer
from .permissions import OwnerOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [OwnerOrReadOnly & IsAuthenticated] 
    http_method_names = ['get', 'post', 'patch', 'delete']


class CategoriesViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [OwnerOrReadOnly & IsAuthenticated] 


class GenresViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [OwnerOrReadOnly & IsAuthenticated] 
