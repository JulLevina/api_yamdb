from django.urls import path

from .views import send_code, get_jwt_token

urlpatterns = [
    path('auth/token/', get_jwt_token, name='user_token'),
    path('auth/signup/', send_code, name='user_sign_up'),
]
