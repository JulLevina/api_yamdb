from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.TextField(max_length=155, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=300, blank=True)
    code = models.CharField(max_length=6, default='000000')

    USER_ROLE = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )

    role = models.CharField(max_length=9, choices=USER_ROLE, default='user')
