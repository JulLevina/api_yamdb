from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    ReviewViewSet,
    CommentViewSet,
    send_code,
    get_jwt_token,
    UserViewSet
)

v1_router = DefaultRouter()

v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
url_auth = [path('token/', get_jwt_token),
            path('signup/', send_code)]

urlpatterns = [
    path('auth/', include(url_auth)),
    path('', include(v1_router.urls)),
]
