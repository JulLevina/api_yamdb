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

    username = kwargs['username']
    email = kwargs['email']
    confirmation_code = kwargs["confirmation_code"]
    message = (
        f'Письмо с кодом для получения токена,'
        f' отправлено пользователю {username},'
        f' на почтовый ящик {email}'
    )
    subject = 'Confirmation_code'
    message_mail = (
        f'Добро пожаловать, {username}!'
        f' Ваш код для получения JWT-токена: {confirmation_code}'
    )
    from_email = None
    recipient_list = (email,)
    send_mail(subject, message_mail, from_email, recipient_list)
    logger.info(message)
