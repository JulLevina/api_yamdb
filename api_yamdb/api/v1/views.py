from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import SendMailSerializer, ApiTokenSerializer
from users.models import User
from users.utils import generate_activation_code, send_mail_in_user


# def generate_activation_code():
#     return ''.join(
#         random.choice(string.ascii_uppercase + string.digits) for x in range(6)
#     )
#
#
# def send_mail_in_user(username, code):
#     user = get_object_or_404(User, username=username)
#     send_mail(
#         'Confirmation_code',
#         f'Добро пожаловать,{user.username}!'
#         f' Ваш код для получения JWT-токена: {code}',
#         'api@mail.ru',
#         [f'{user.email}']
#     )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_code(request):
    serializer = SendMailSerializer(data=request.data)
    email = request.data.get('email', False)
    username = request.data.get('username', False)
    if serializer.is_valid():
        code = generate_activation_code()
        user = User.objects.filter(email=email).exists()
        if not user:
            User.objects.create_user(email=email, username=username)
        User.objects.filter(email=email).update(
            code=make_password(code, salt=None, hasher='default')
        )
        send_mail_in_user(username, code)
        return Response(f'Код отправлен на адрес {email}', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = ApiTokenSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.data.get('email')
        code = serializer.data.get('code')
        user = get_object_or_404(User, email=email)
        if check_password(code, user.code):
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response({'code': 'Неверный код подтверждения'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
