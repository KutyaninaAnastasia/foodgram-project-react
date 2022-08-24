from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet, IngredientViewSet, RecipeViewSet,
                    DownloadShoppingCart)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         DownloadShoppingCart.as_view(), name='download_shoppinglist'),
    path('', include(router.urls)),
]
