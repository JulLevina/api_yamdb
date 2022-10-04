from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserAuthSerializer(serializers.ModelSerializer):
    """Сериализатор для авторизации пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise ValidationError('Пользователь c таким именем существует')
        if data['username'] == 'me':
            raise ValidationError(
                'Пользователь c таким именем нельзя зарегистрировать'
            )
        if User.objects.filter(email=data['email']).exists():
            return ValidationError(
                'Такая электронная почта уже зарегистрирована'
            )
        return data
