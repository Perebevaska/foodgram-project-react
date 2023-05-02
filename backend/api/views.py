from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (CartList, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.models import User

from .permissions import AuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagsSerializer


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
    permission_classes = (AuthorOrReadOnly,)

    def add(self, model, user, pk, name):
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if relation.exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite(self, request, pk=None):
        "Добавление и удаление рецепта из избранного."""
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            try:
                response = self.add(Favorite, user, pk, name)
                return response
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'избранного':
            name = 'favorites'
            try:
                response = self.delete_relation(Favorite, user, pk, name)
                return response
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





