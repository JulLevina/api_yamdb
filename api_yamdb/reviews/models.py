from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.db import models

ANONYMOUS_USER_ID = 1


class User(AbstractUser):
    pass


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.IntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)])
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self) -> str:
        return self.text


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField(
        verbose_name='Дата публикации'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        'Genre',
        through='TitleGenre',
        verbose_name='жанр'
    )
    category = models.ForeignKey(
        'Category',
        default=ANONYMOUS_USER_ID,
        on_delete=models.SET_DEFAULT,
        related_name='titles',
        verbose_name='категория'
    )

    class Meta:
        ordering = ['-year']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name
    
    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg('score'))['score__avg']


class TitleGenre(models.Model):
    genre = models.ForeignKey(
        'Genre',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='жанр'
    )
    title = models.ForeignKey(
        Title,
        default=ANONYMOUS_USER_ID,
        on_delete=models.SET_DEFAULT,
        related_name='genres',
    )


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='slug'
    )

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug'
    )
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self) -> str:
        return self.text
