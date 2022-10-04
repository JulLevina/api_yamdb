from django.contrib import admin

from .models import Title, Genre, Category, Review, Comment


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description', 'genre', 'category')
    search_fields = ('name', 'year')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'created'
    )
    list_filter = ('author',)


admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Comment)
