from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from fpdf import FPDF
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.filters import RecipeFilter
from recipes.ingr_filters import CustomSearchFilter
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from recipes.permissions import AuthorOrReadOnly
from recipes.serializers import (IngredientSerializer, RecipeSerializer,
                                 SmallRecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add(self, model, user, pk, name):
        """Добавление рецепта в список пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk, name):
        """"Удаление рецепта из списка пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'Нельзя повторно удалить рецепт из {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self._add_to_favorite(user, pk)
        elif request.method == 'DELETE':
            return self._delete_from_favorite(user, pk)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _add_to_favorite(self, user, pk):
        name = 'избранное'
        return self.add(Favorite, user, pk, name)

    def _delete_from_favorite(self, user, pk):
        name = 'избранного'
        return self.delete_relation(Favorite, user, pk, name)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self._add_to_shopping_cart(user, pk)
        elif request.method == 'DELETE':
            return self._delete_from_shopping_cart(user, pk)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _add_to_shopping_cart(self, user, pk):
        name = 'список покупок'
        return self.add(ShoppingCart, user, pk, name)

    def _delete_from_shopping_cart(self, user, pk):
        name = 'списка покупок'
        return self.delete_relation(ShoppingCart, user, pk, name)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_cart(self, request):
        """Формирование и скачивание списка покупок."""
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__sh_cart__user=user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    Sum('amount', distinct=True))
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            'Shentox', '', './backend/fonts/Shentox.ttf', uni=True)
        pdf.set_font('Shentox', size=12)
        pdf.cell(txt='Список покупок', center=True)
        pdf.ln(10)
        for i, ingredient in enumerate(ingredients):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount__sum']
            pdf.cell(30, 10, f'{i + 1}) {name} - {amount} {unit}')
            pdf.ln()
        file = pdf.output(dest='S')
        response = HttpResponse(
            content_type='application/pdf', status=status.HTTP_200_OK)
        response['Content-Disposition'] = (
            'attachment; filename="список_покупок.pdf"')
        response.write(bytes(file))
        return response
