from rest_framework import serializers

from v1.models import Title, Genre, Category


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')
 

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
