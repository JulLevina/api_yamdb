from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """
    Возвращает JSON-данные всех полей модели Category
    для эндпоинта api/v1/categories/.
    """

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """
    Возвращает JSON-данные всех полей модели Genre
    для эндпоинта api/v1/genres/.
    """

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """Только для чтения данных.
    Возвращает JSON-данные всех полей модели Title
    для эндпоинта api/v1/titles/.
    Добавляет новое поле rating.
    """

    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating'
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Только для записи данных.
    Возвращает JSON-данные всех полей модели Title
    для эндпоинта api/v1/titles/.
    """

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """
    Возвращает JSON-данные всех полей модели Reviews
    для эндпоинта api/v1/titles/{title_id}/reviews/.
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        model = Review

    def validate(self, data):
        """Проверка невозможности дважды оставить отзыв на произведение."""
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        author = self.context['request'].user
        if Review.objects.filter(author=author, title_id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Возаращает JSON-данные всех полей модели Comment
    для эндпоинта api/v1/titles/{title_id}/reviews/{review_id}/commrnts.
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = (
            'id',
            'author',
            'text',
            'pub_date'
        )
        model = Comment


class SendMailSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя и отправки кода."""

    username_validator = UnicodeUsernameValidator()

    username = serializers.CharField(
        validators=[username_validator],
    )
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate_username(self, value):
        """Проверка, соответствия username на допустимость."""
        if value.lower() == settings.RESERVED_NAME:
            raise serializers.ValidationError(
                {'detail': 'Данное имя использовать запрещено!'}
            )
        return value


class ApiTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для отправки токена зарегистрированному пользователю."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели класса User."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
