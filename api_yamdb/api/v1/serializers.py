from unicodedata import category
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserSerializer

from reviews.models import Title, Genre, Category, Review, Comment, User


class TitleSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    def get_average_rating(self, obj):
        return int(obj.average_rating)

    class Meta:
        fields = (
            'name',
            'year',
            'description',
            'genre',
            'category',
            'average_rating'
        )
        model = Title


class GenreSerializer(serializers.ModelSerializer):
    # genre_name = serializers.CharField(source='name')

    class Meta:
        fields = (
            'name',  # genre_name
            'slug'
        )
        model = Genre

class CategorySerializer(serializers.ModelSerializer):
    # category_name = serializers.CharField(source='name')
    # category_slug = serializers.SlugField(source='slug')

    class Meta:
        fields = (
            'name',  # category_name
            'slug'  # category_slug
        )
        model = Category


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
            'title',
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
        fields = 'text'
        read_only_fields = ('review',)
        model = Comment
