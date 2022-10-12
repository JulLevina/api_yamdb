from django.db import models
from django.contrib.auth.models import AbstractUser

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.TextField(
        'Пароль',
        max_length=155,
        unique=True
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True
    )
    bio = models.TextField(
        'Биография',
        max_length=300,
        blank=True
    )
    confirmation_code = models.CharField(
        'Код активации',
        max_length=78,
        default='000000'
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=9,
        choices=ROLES,
        default='user'
    )
    is_active = models.BooleanField(
        'Активирован',
        default=True
    )

    def __str__(self):
        return self.username
