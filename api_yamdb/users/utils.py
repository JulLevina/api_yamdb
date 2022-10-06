import random
import string

from django.core.mail import send_mail
from rest_framework.generics import get_object_or_404

from .models import User


def generate_activation_code():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(6)
    )


def send_mail_in_user(username, confirmation_code):
    user = get_object_or_404(User, username=username)
    send_mail(
        'Confirmation_code',
        f'Добро пожаловать, {user.username}!'
        f' Ваш код для получения JWT-токена: {confirmation_code}',
        'api@mail.ru',
        [f'{user.email}']
    )
    print(f'Письмо отправленно пользователю {user.username},'
          f' на почтовый ящик {user.email}')
