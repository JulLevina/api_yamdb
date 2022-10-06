from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import UserAdminOnly
from .serializers import SendMailSerializer, ApiTokenSerializer, \
    UsersSerializer, UserMeSerializer
from users.models import User
from users.utils import generate_activation_code, send_mail_in_user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
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
@permission_classes([permissions.AllowAny])
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


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, UserAdminOnly)
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        if self.request.method == 'PATCH':
            user = self.request.user
            serializer = UserMeSerializer(user, data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                username=self.request.user.username,
                email=self.request.user.email
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = self.request.user
        serializer = UserMeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)