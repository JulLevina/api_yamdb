from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User


class SendMailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

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


class ApiTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
