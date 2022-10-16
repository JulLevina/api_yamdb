import os
import csv

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import Title, Genre, Category, Review, Comment, TitleGenre
from users.models import User

DATA_LIST = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    User: 'users.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv'
}


class Command(BaseCommand):
    """Загружает csv-данные в базу данных."""

    def handle(self, *args, **kwargs):
        call_command('migrate')
        for model, csv_data in DATA_LIST.items():
            with open(os.path.join(settings.BASE_DIR,
                      f'static/data/{csv_data}'),
                      'r', encoding='utf8') as file_scv:
                csv_reader = csv.DictReader(file_scv)
                model.objects.bulk_create(model(**data) for data in csv_reader)
