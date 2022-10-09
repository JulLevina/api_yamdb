from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from djoser.serializers import UserSerializer

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
    average_rating = serializers.SerializerMethodField()
    category=CategorySerializer(read_only=True)
    genre=GenreSerializer(many=True)
    
    def get_average_rating(self, obj):
        return int(obj.average_rating)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'average_rating'
        )
        model = Title


class CreateTitleSerializer(serializers.ModelSerializer):
    category=serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre=serializers.SlugRelatedField(
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
        read_only_fields = ('title',)
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'text'),
                message=( 
                    'Отзыв на указанное произведение '
                    'уже Вами опубликован.'
                ) 
            )
        ]


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
