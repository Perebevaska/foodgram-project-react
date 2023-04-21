from djoser.views import UserViewSet
from users.models import User
from recipes.models import Tag, Ingredient, Recipe
from rest_framework import viewsets
from .serializers import CustomUserSerializer, TagsSerializer, IngredientSerializer, RecipeSerializer

class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


