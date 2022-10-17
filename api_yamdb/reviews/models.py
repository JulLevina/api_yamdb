from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User
from api.v1.validators import validate_year


class Review(models.Model):
    """Модель, определяющая состав полей отзывов на произведение."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                'Максимально низкая оценка %(limit_value)s!'
            ),
            MaxValueValidator(
                10,
                'Максимально высокая оценка %(limit_value)s!'
            )
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self) -> str:
        return self.text[:settings.SHOW_REVIEW_NUMBER_OF_CHARACTERS]


class Title(models.Model):
    """Модель, определяющая состав полей произведения."""

    name = models.TextField(verbose_name='Название произведения')
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        verbose_name='Год создания'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        'Genre',
        through='TitleGenre',
        related_name='genre',
        verbose_name='Жанры'
    )
    category = models.ForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='category',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name


class TitleGenre(models.Model):
    """Модель, необходимая для связи жанра и произведения."""

    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Category(models.Model):
    """Модель, определяющая состав полей категории произведения."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Модель, определяющая состав полей жанра произведения."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    """"Модель, определяющая состав полей комментариев к отзывам."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self) -> str:
        return self.text[:settings.SHOW_COMMENT_NUMBER_OF_CHARACTERS]
