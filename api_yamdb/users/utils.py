import logging

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

MESSAGE = (
    'Письмо с кодом для получения токена,'
    ' отправлено пользователю {username},'
    ' на почтовый ящик {email}'
)
MESSAGE_MAIL = (
    'Добро пожаловать, {username}! Ваш код для получения JWT-токена:'
    '{confirmation_code}'
)


def generate_activation_code(user):
    """Генератор кода для получения Токена."""

    return default_token_generator.make_token(user)


def token_verification(user, confirmation_code):
    """Проверка соответствия кода и пользователя"""

    return default_token_generator.check_token(user, confirmation_code)


def send_mail_in_user(username, email, confirmation_code):
    """Функция отправки письма пользователю."""
    send_mail(
        subject='Confirmation_code',
        message=MESSAGE_MAIL.format(
            username=username,
            confirmation_code=confirmation_code,
        ),
        from_email=None,
        recipient_list=[email]
    )
    logger.info(MESSAGE.format(
        username=username,
        email=email,
    ))
