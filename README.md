# __API проекта Api_Yamdb (v1)__
## _Описание_

API для Yatube - это проект, позволяющий собирать отзывы пользователей на различные произведения.

#### _Технологии_

- Python 3.7
- Django 2.2.16
- DRF 3.12.4

#### _Запуск проекта в dev-режиме_

- Установите и активируйте виртуальное окружение
```
py3.7 -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- Создайте и выполните миграции
```
python manage.py makemigrations
```
```
python manage.py migrate
```
- В папке с файлом manage.py выполните команду для заполнения базы данных тестовыми данными:
```
python manage.py csv_command
```
- а затем выполните команду:
```
python3 manage.py runserver
```

#### _Алгоритм регистрации пользователей_
1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email и username на эндпоинт /api/v1/auth/signup/.
2. YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
3. Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).
4. При желании пользователь отправляет PATCH-запрос на эндпоинт /api/v1/users/me/ и заполняет поля в своём профайле (описание полей — в документации).

- Запрос на регистрацию пользователя:
```
POST auth/signup/
```
```
body:
{
    "username": "Test_User",
    "email": "Test_email@test.ru"
}
```
- вернет следующий ответ
```
{
    "username": "Test_User",
    "email": "Test_email@test.ru"
}
```

#### _Примеры запросов к API для неавторизованных пользователей_
Неавторизованные пользователи могут просматривать описания произведений, читать отзывы и комментарии.
- Пример запроса на получения информации о произведении по id:
```
GET api/v1/titles/{titles_id}/
```
- Ответ:
```
{
    "id": 0,
    "name": "string",
    "year": "test_text",
    "rating": "string"
    "description": "string",
    "genre": [
        {...}
    ],
    "category": {
    "name": "string",
    "slug": "string"
    }
}
```

#### _Примеры запросов к API для авторизованных пользователей_
Авторизованные пользователи наделены правом создания, изменения и удаления отзывов и комментариев, авторами которого они являются.
- Для авторизации зарегистрированному пользователю, получившему на указанную при регистрации эл.почту код подтверждения, необходимо получить JWT-токен с помощью следующего запроса
```
POST api/v1/auth/token/
```
```
body:
{
    "username": "Test_User",
    confirmation_code": "string"
}
```

"access" - поле, содержащее токен.

- Запрос на создание отзыва на произведение:
```
POST api/v1/titles/{titles_id}/reviews/
```
```
body:
{
    "text": "string",
    "score": 1
}
```
- вернет следующий ответ
```
{
    "id": 0,
    "text": "string",
    "author": "string",
    "score": 1,
    "pub_date": "2019-08-24T14:15:22Z"
}
```
- С примерами других запросов можно ознакомиться в [документации](http://127.0.0.1:8000/redoc/)
- Подробнее про установку DRF можно почитать [здесь](https://github.com/encode/django-rest-framework/blob/master/README.md )

## _Лицензия_

MIT

## _Разработчики_
[Левина Юля](https://github.com/JulLevina), [Андрей Пахомов](https://github.com/pakhem), [Антон Плотицын](https://github.com/Anton0530212)
