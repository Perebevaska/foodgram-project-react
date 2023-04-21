from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet


router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]