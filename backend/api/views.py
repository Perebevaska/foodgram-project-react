from djoser.views import UserViewSet
from users.models import User
from recipes.models import Tag, Ingredient, Recipe
from rest_framework import viewsets
from .serializers import  TagsSerializer, IngredientSerializer, RecipeSerializer, CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import AdminOrReadOnly

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AdminOrReadOnly, )


