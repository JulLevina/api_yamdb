from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверка невозможности указать год больше текущего."""
    if value > timezone.now().year:
        raise ValidationError('Проверьте год создания!')
