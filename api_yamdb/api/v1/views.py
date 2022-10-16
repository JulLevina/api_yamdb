from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Title, Genre, Category, Review
from users.models import User
from users.utils import (
    generate_activation_code,
    send_mail_in_user,
    token_verification,
)
from api.v1.serializers import (
    TitleReadSerializer,
    TitleWriteSerializer,
    GenreSerializer,
    CategorySerializer,
    ReviewSerializer,
    CommentSerializer,
    SendMailSerializer,
    ApiTokenSerializer,
    UserSerializer,
)
from api.v1.permissions import AdminOnly, IsAuthorOrStaffOrReadOnly, ReadOnly
from api.v1.filters import TitleFilter


class TitleViewSet(viewsets.ModelViewSet):
    """Выполняет все операции с произведениями.
    Обрабатывает все запросы для эндпоинта api/v1/titles/.
    """

    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).select_related('category').order_by('category__name', '-rating')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return TitleWriteSerializer
        return TitleReadSerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Выполняет все операции с жанрами.
    Обрабатывает все запросы для эндпоинта api/v1/genres/.
    """

    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Genre.objects.order_by('name')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ Позволяет получить список, создать или удалить категорию.
    Обрабатывает все запросы для эндпоинта api/v1/categories/.
    """

    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Выполняет все операции с отзывами.
    Обрабатывает запросы 'get', 'post', 'patch', 'delete'
    для эндпоинта api/v1/titles/{title_id}/reviews.
    """

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.select_related(
            'author').order_by('pub_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Выполняет все операции с комментариями.
    Обрабатывает запросы 'get', 'post', 'patch', 'delete' для
    эндпоинта api/v1/titles/{title_id}/reviews/{review_id}/comments.
    """

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_review(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        return get_object_or_404(Review, pk=review_id, title_id=title_id)

    def get_queryset(self):
        return self.get_review().comments.order_by('pub_date')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


@api_view(('POST',))
@permission_classes((AllowAny,))
def send_code(request,):
    """Функция регистрации пользователя и отправки кода подтверждения."""
    serializer = SendMailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    try:
        user, created = User.objects.get_or_create(
            email=email, username=username
        )
    except IntegrityError:
        return Response(
            {'username': 'Пользователь с таким именем или почтой уже есть'},
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = generate_activation_code(user)
    send_mail_in_user(
        username=username,
        email=email,
        confirmation_code=confirmation_code
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((AllowAny,))
def get_jwt_token(request,):
    """Функция проверки кода подтверждения и выдачи токена."""
    serializer = ApiTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if token_verification(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Класс предоставления информации о пользователях."""

    queryset = User.objects.order_by('username')
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    search_fields = ('^username',)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
