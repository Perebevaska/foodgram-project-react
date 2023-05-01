from djoser.views import UserViewSet
from users.models import User
from recipes.models import Tag, Ingredient, Recipe, Favorite, IngredientAmount,CartList
from rest_framework import viewsets
from .serializers import TagsSerializer, IngredientSerializer, RecipeSerializer
from rest_framework.permissions import AllowAny
from .permissions import AuthorOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response



from .permissions import AuthorOrReadOnly
from .serializers import RecipeSerializer, SmallRecipeSerializer

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





