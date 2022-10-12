import datetime as dt

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)

    def get_rating(self, obj):
        rating = obj.average_rating
        if not rating:
            return rating
        return round(rating, 1)

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


class CreateTitleSerializer(serializers.ModelSerializer):
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
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год создания!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
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
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        author = self.context['request'].user
        if self.context['request'].method == 'POST':
            if Review.objects.filter(author=author, title=title_id).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на данное произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
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
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate(self, data):
        if data['username'] == 'me':
            raise ValidationError(
                'Пользователя c таким именем нельзя зарегистрировать'
            )
        if User.objects.filter(
                username=data['username'],
                is_active=True
        ).exists():
            raise ValidationError('Пользователь c таким именем существует')
        if User.objects.filter(
                email=data['email'], is_active=True).exists():
            raise ValidationError(
                'Такая электронная почта уже зарегистрирована'
            )
        return data


class ApiTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',)
