from rest_framework.routers import DefaultRouter
from django.urls import path, include

from api.views import TitleViewSet, GenreViewSet, CategoryViewSet, ReviewViewSet, CommentViewSet  # UserViewSet

v1_router = DefaultRouter()

v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet, basename='categories')
# v1_router.register('users', UserViewSet, basename='users') 
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(r'reviews/(?P<review_id>\d+)/comments',
                   CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(v1_router.urls)),
    # path('signup/', views.SignUp.as_view(), name='signup'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
