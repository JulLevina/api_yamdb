from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import user_sign_up

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'auth/signup/',
        user_sign_up,
        name='user_sign_up'
    ),
]
