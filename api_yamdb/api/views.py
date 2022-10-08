from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import views
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Genre, Category, Review, User
from api.v1.serializers import(
    TitleSerializer,
    GenreSerializer,
    CategorySerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer
)
from api.v1.permissions import IsAuthorOrReadOnly


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    def get_queryset(self):
        return Title.objects.annotate(_average_rating=Avg('reviews__score'))  # order_by('-score_avg')


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly, IsAdminUser)
    pagination_class = LimitOffsetPagination
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly, IsAdminUser)
    pagination_class = LimitOffsetPagination
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
