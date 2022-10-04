from unicodedata import category
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Title, Genre, Category, Review, Comment


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'year',
            'description',
            'genre',
            'category'
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
    category_name = serializers.CharField(source='name')
    category_slug = serializers.SlugField(source='slug')

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
            'text',
            'score'
        )
        read_only_fields = ('title',)
        model = Review
    
    # def get_rating(self, obj):
    #     return sum(obj.score) // obj.score.count()


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
