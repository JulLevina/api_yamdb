from django.urls import path, include
from rest_framework import routers


from .views import send_code, get_jwt_token, UserViewSet

router_users_v1 = routers.DefaultRouter()
router_users_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/', get_jwt_token, name='user_token'),
    path('auth/signup/', send_code, name='user_sign_up'),
    path('', include(router_users_v1.urls)),
]
