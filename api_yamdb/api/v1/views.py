from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Title, Genre, Category, Review
from users.models import User
from users.utils import generate_activation_code, send_mail_in_user
from users.utils import token_verification

from api.v1.serializers import TitleReadSerializer, TitleWriteSerializer
from api.v1.serializers import GenreSerializer, CategorySerializer
from api.v1.serializers import ReviewSerializer, CommentSerializer
from api.v1.serializers import SendMailSerializer, ApiTokenSerializer, UserSerializer
   
from api.v1.permissions import AdminOnly, IsAuthorOrStaffOrReadOnly, ReadOnly
from api.v1.filters.title_filters import TitleGenreFilter


class TitleViewSet(viewsets.ModelViewSet):
    """Выполняет все операции с произведениями.

    Обрабатывает все запросы для эндпоинта api/v1/titles/.
    """

    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).select_related('category').order_by('category__name', '-rating')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleGenreFilter

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
    queryset = Genre.objects.all()
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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """Выполняет все операции с отзывами.
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

    def get_title_and_review_id(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id, title_id=title_id)

    def get_queryset(self):
        return (
            self.get_title_and_review_id().comments.all().order_by('pub_date')
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_title_and_review_id()
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_code(request):
    """Функция регистрации пользователя и отправки кода подтверждения."""

    serializer = SendMailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    user, created = User.objects.get_or_create(
        email=email, username=username
    )
    confirmation_code = generate_activation_code(user)
    user.save()
    send_mail_in_user(username, email, confirmation_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """Функция проверки кода подтверждения и выдачи токена."""
    serializer = ApiTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if token_verification(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Класс предоставления информации о пользователях."""
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
        if request.method == 'GET':
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
