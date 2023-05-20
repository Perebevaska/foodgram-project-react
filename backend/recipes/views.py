import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Sum
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.translation import gettext_lazy as _
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
        relation = model.objects.filter(user=user, recipe=recipe)
        if relation.exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk, name):
        """"Удаление рецепта из списка пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': f'Нельзя повторно удалить рецепт из {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            url_name='favorite')
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов - Избранное."""
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            return self.add(Favorite, user, pk, name)
        if request.method == 'DELETE':
            name = 'избранного'
            return self.delete_relation(Favorite, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов - Список покупок."""
        user = request.user
        if request.method == 'POST':
            name = 'список покупок'
            return self.add(ShoppingCart, user, pk, name)
        if request.method == 'DELETE':
            name = 'списка покупок'
            return self.delete_relation(ShoppingCart, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_cart(self, request):
        """Формирование и скачивание списка покупок."""
        user = request.user
        ingredients = get_list_or_404(
            IngredientAmount.objects.filter(recipe__sh_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount')))
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            'Shentox', '', os.path.join(
                settings.BASE_DIR,
                'fonts/Shentox.ttf'
            ), uni=True)
        pdf.set_font('Shentox', size=12)
        pdf.cell(txt=_('Shopping List'), center=True)
        pdf.ln(8)
        for i, ingredient in enumerate(ingredients):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            pdf.cell(30, 15, f'{i + 1}) {name} - {amount} {unit}')
            pdf.ln()
        file = pdf.output(dest='S')
        filename = 'shopping_cart.pdf'
        path = default_storage.save(filename, ContentFile(bytes(file)))
        if not path:
            raise ImproperlyConfigured(_('Could not save file %s') % filename)
        url = default_storage.url(path)
        return Response({'url': url}, status=status.HTTP_200_OK)
