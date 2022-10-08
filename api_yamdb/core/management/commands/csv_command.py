import os
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import Title, Genre, Category, Review, Comment, TitleGenre, User

DATA_LIST = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    # User: 'users.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

class Command(BaseCommand):
    """Загружает csv-данные в базу данных."""
    
    def handle(self, *args, **options):
        for model, scv_data in DATA_LIST.items():
            with open(os.path.join(settings.BASE_DIR, f'static/data/{scv_data}'), 'r', encoding='utf8') as file_scv:
                csv_reader = csv.DictReader(file_scv)
                model.objects.bulk_create(model(**data) for data in csv_reader)

        # rows = []
        # with open(os.path.join(settings.BASE_DIR, 'static/data/category.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     next(csv_reader)
        #     for row in csv_reader:
        #         category, _ = Category.objects.get_or_create(
        #             id=row['id'],
        #             name=row['name'],
        #             slug=row['slug']
        #         )
        #         category.save()

        # with open(os.path.join(settings.BASE_DIR, 'static/data/genre.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         genre, _ = Genre.objects.get_or_create(
        #             id=row['id'],
        #             name=row['name'],
        #             slug=row['slug']
        #         )
        #         genre.save()
        
        # with open(os.path.join(settings.BASE_DIR, 'static/data/users.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         author, _ = User.objects.get_or_create(
        #             id=row['id'],
        #             username=row['username']
        #         )
        #         author.save()

        # with open(os.path.join(settings.BASE_DIR, 'static/data/titles.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         title, _ = Title.objects.get_or_create(
        #             id=row['id'],
        #             name=row['name'],
        #             year=row['year'],
        #             category=category
        #         )
        #         title.save()
        
        # with open(os.path.join(settings.BASE_DIR, 'static/data/genre_title.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         genre_title, _ = TitleGenre.objects.get_or_create(
        #             id=row['id'],
        #             title=title,
        #             genre=genre
        #         )
        #         genre_title.save()

        # with open(os.path.join(settings.BASE_DIR, 'static/data/review.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         review, _ = Review.objects.get_or_create(
        #             id=row['id'],
        #             title=title,
        #             text=row['text'],
        #             author=author,
        #             score=int(row['score']),
        #             pub_date=row['pub_date']
        #         )
        #         review.save()

        # with open(os.path.join(settings.BASE_DIR, 'static/data/comments.csv'), encoding='utf8') as file_scv:
        #     csv_reader = csv.DictReader(file_scv, delimiter=',')
        #     for row in csv_reader:
        #         comment, _ = Comment.objects.get_or_create(
        #             id=row['id'],
        #             author=author,
        #             review=review,
        #             text=row['text'],
        #             pub_date=row['pub_date']
        #         )
        #         comment.save()
