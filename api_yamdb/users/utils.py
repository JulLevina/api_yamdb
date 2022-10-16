import logging

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def generate_activation_code(user):
    """Генератор кода для получения Токена."""

    return default_token_generator.make_token(user)


def token_verification(user, confirmation_code):
    """Проверка соответствия кода и пользователя"""

    return default_token_generator.check_token(user, confirmation_code)


def send_mail_in_user(**kwargs):
    """Функция отправки письма пользователю."""

    message = (
        f'Письмо с кодом для получения токена,'
        f' отправлено пользователю {kwargs["username"]},'
        f' на почтовый ящик {kwargs["email"]}'
    )
    send_mail(
        'Confirmation_code',
        f'Добро пожаловать, {kwargs["username"]}!'
        f' Ваш код для получения JWT-токена: {kwargs["confirmation_code"]}',
        None,
        [f'{kwargs["email"]}']
    )
    logger.info(message)
