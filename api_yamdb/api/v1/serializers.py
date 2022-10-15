from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from rest_framework import serializers

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)

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

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError('Проверьте год создания!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Возаращает JSON-данные всех полей модели Reviews
    для эндпоинта api/v1/titles/{title_id}/reviews/
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
    для эндпоинта api/v1/titles/{title_id}/reviews/{review_id}/commrnts
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
    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate(self, data):
        """Проверка, соответствия username и email на допустимость."""
        email = data.get('email')
        username = data.get('username')
        duplicate_email = (
            User.objects.filter(Q(email=email))
            .filter(~Q(username=username))
            .exists()
        )
        duplicate_username = (
            User.objects.filter(Q(username=username))
            .filter(~Q(email=email))
            .exists()
        )
        if duplicate_email:
            raise serializers.ValidationError(
                {'detail': 'Такой email адрес уже зарегистрирован.'}
            )
        if duplicate_username:
            raise serializers.ValidationError(
                {'detail': 'Такое имя пользователя уже используется.'}
            )
        if username in settings.RESERVED_NAME:
            raise serializers.ValidationError(
                {'detail': 'Данное имя использовать запрещено!'}
            )
        return data


class ApiTokenSerializer(serializers.Serializer):
    """Сериализатор для отправки токена зарегистрированному пользователю."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'email')


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

    def validate_role(self, role):
        """Запрещает не админу менять роль."""
        try:
            if self.instance.role != 'admin':
                return self.instance.role
            return role
        except AttributeError:
            return role
