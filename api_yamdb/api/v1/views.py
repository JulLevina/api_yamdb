from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Title, Genre, Category, Review
from users.models import User
from users.utils import generate_activation_code, send_mail_in_user
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
from core.filters.title_filters import TitleGenreFilter


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Title.objects.annotate( 
               rating=Avg('reviews__score') 
               ).select_related('category').order_by('category__name', '-rating')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleGenreFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleWriteSerializer
        return TitleReadSerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Genre.objects.all().order_by('name')
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
    permission_classes = (AdminOnly | ReadOnly,)
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)


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
