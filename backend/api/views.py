from api.permissions import AuthorOrReadOnly
from django.core.cache import cache
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from fpdf import FPDF
from recipes.filters import NameFilter
from recipes.models import (CartList, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from backend.settings import (PDF_CELL_HEIGHT, PDF_CELL_LENTGH, PDF_FONT_NAME,
                              PDF_FONT_PATH, PDF_FONT_SIZE, PDF_LENTGH)

from recipes.filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeWithImageSerializer, SubscriptionSerializer,
                          TagsSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """
        Список авторов, на которых подписан пользователь.
        """
        user = request.user
        queryset = user.follower.all().select_related('author')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """
        Подписка на автора.
        """
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'На себя нельзя подписаться / отписаться'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription, created = Subscription.objects.get_or_create(
            author=author, user=user
        )
        if request.method == 'DELETE':
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionSerializer(
            subscription, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    search_fields = ('^name',)
    filter_backends = (NameFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add(self, model, user, pk, name):
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if relation.exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeWithImageSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk, name):
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': f'Рецепт уже удален из {name}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite(self, request, pk=None):
        "Добавление и удаление рецепта из избранного." ""
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            try:
                response = self.add(Favorite, user, pk, name)
                return response
            except ValueError as e:
                return Response(
                    {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'избранного':
            name = 'favorites'
            try:
                response = self.delete_relation(Favorite, user, pk, name)
                return response
            except ValueError as e:
                return Response(
                    {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Invalid request method.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'POST':
            name = 'Cписок покупок'
            return self.add(CartList, user, pk, name)

        if request.method == 'DELETE':
            name = 'Cписка покупок'
            if not CartList.objects.filter(pk=pk, user=user).exists():
                return Response(
                    {'error': 'Список покупок не найден'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return self.delete_relation(CartList, user, pk, name)

    # def get_ingredients(self, user):
    #     return IngredientAmount.objects.filter(
    #         recipe__sh_cart__user=user).values(
    #             'ingredient__name', 'ingredient__measurement_unit').annotate(
    #                 Sum('amount', distinct=True))

    # пробую кеширование
    def get_ingredients(self, user):
        cache_key = f'ingredients_user_{user.id}'
        ingredients = cache.get(cache_key)
        if ingredients is None:
            ingredients = (
                IngredientAmount.objects.filter(recipe__sh_cart__user=user)
                .values('ingredient__name', 'ingredient__measurement_unit')
                .annotate(Sum('amount', distinct=True))
            )
            cache.set(cache_key, ingredients)
        return ingredients

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = self.get_ingredients(user)
        if not ingredients:
            return Response(
                {'error': 'Список покупок пуст'},
                status=status.HTTP_404_NOT_FOUND,
            )
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(PDF_FONT_NAME, '', PDF_FONT_PATH, uni=True)
        pdf.set_font(PDF_FONT_NAME, size=PDF_FONT_SIZE)
        pdf.cell(txt='Список покупок', center=True)
        pdf.ln(PDF_LENTGH)
        for i, ingredient in enumerate(ingredients):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount__sum']
            pdf.cell(
                PDF_CELL_LENTGH,
                PDF_CELL_HEIGHT,
                f'{i + 1}) {name} - {amount} {unit}'
            )
            pdf.ln()
        file = pdf.output(dest='S')
        response = HttpResponse(
            content_type='application/pdf', status=status.HTTP_200_OK
        )
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.pdf"'
        response.write(bytes(file))
        return response
