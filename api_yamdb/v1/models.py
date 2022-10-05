from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CHOICES = (
    ('Movies','Фильмы'),
    ('Books', 'Книги'),
    ('Music','Музыка'),
)

ANONYMOUS_USER_ID = 1


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256) 
    year = models.IntegerField(verbose_name='Дата публикации')
    description = models.TextField(verbose_name='Описание')
    genre = models.ForeignKey(
        'Genres',
        on_delete=models.PROTECT,
        related_name='title',
    #     blank=True,
        null=True,
    #     verbose_name='жанр'
    )
    cat = models.ForeignKey(
        'Categories',
    #     # default=ANONYMOUS_USER_ID,
        on_delete=models.PROTECT,
    #     related_name='titles',
    #     verbose_name='категория',
        null = True
    )

    # class Meta:
    #     ordering = ('name',)
    #     verbose_name = 'Исполнитель'
    #     verbose_name_plural = 'Исполнители'

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=256,choices=CHOICES,
        verbose_name='Название категории')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='slug')

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='Описание')

    # class Meta:
    #     ordering = ('name',)
    #     verbose_name = 'Жанр'
    #     verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name
