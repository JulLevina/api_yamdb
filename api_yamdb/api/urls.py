from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TitleViewSet, CategoriesViewSet, GenresViewSet

app_name = 'api'

router = DefaultRouter()
router.register('titles', TitleViewSet)
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
]
