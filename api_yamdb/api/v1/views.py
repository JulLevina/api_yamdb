from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework_simplejwt.tokens import AccessToken
from uritemplate import partial

from reviews.models import Title, Genre, Category, Review
from users.models import User
from users.utils import generate_activation_code, send_mail_in_user
from .serializers import (
    TitleSerializer,
    CreateTitleSerializer,
    GenreSerializer,
    CategorySerializer,
    ReviewSerializer,
    CommentSerializer,
    SendMailSerializer,
    ApiTokenSerializer,
    UserSerializer,
)
from .permissions import (
    IsAuthorOrReadOnly,
    AdminOnly,
    IsStaffOrReadOnly,
    ReadOnly,
)


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsStaffOrReadOnly | ReadOnly,)
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    # filter_backends =
    # search_fields =

    def get_queryset(self):
        return Title.objects.annotate(
            _average_rating=Avg('reviews__score'))  # order_by('-score_avg')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateTitleSerializer
        return TitleSerializer


class GenreViewSet(viewsets.ModelViewSet):
    permission_classes = (IsStaffOrReadOnly | ReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(detail=False, methods=['delete'], url_path=r'(?P<slug>\w+)',
            lookup_field='slug')
    def genre_delete(self, request, slug):
        genre = self.get_object()
        serializer = GenreSerializer(genre)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsStaffOrReadOnly | ReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(detail=False, methods=['delete'], url_path=r'(?P<slug>\w+)',
            lookup_field='slug')
    def category_delete(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (
    IsAuthenticatedOrReadOnly | IsAuthorOrReadOnly | AdminOnly,)
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    # def partial_update(self, request, *args, **kwargs):
    #     serializer = ReviewSerializer(request.user, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly | AdminOnly,)
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data,
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_code(request):
    serializer = SendMailSerializer(data=request.data)
    email = request.data.get('email', False)
    username = request.data.get('username', False)
    if serializer.is_valid():
        confirmation_code = generate_activation_code()
        user = User.objects.filter(username=username, is_active=False).exists()
        if not user:
            User.objects.create_user(email=email, username=username)
        User.objects.filter(username=username).update(
            confirmation_code=make_password(confirmation_code,
                                            salt=None, hasher='default'
                                            ), is_active=True
        )
        send_mail_in_user(username, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = ApiTokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Неверный код подтверждения'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    search_fields = ('^username',)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if 'role' in request.data:
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data)
