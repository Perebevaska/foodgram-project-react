# from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from recipes.validators import validate_ingredients, validate_tags
from users.serializers import CustomUserSerializer
from django.db import transaction


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit'
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class SmallRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientAmountSerializer(
        read_only=True, many=True, source='ingredientamount_set')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, является ли рецепт избранным
        для пользователя, который отправил запрос."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_id = request.user.id
            return Favorite.objects.filter(
                user=user_id, recipe=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, есть ли рецепт в корзине
        покупок пользователя, который отправил запрос."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_id = request.user.id
            return ShoppingCart.objects.filter(
                user=user_id, recipe=obj.id).exists()
        return False

    def create_ingredient_amount(self, valid_ingredients, recipe):
        """Создает записи в модели IngredientAmount
        для указанного количества ингредиентов."""
        ingredient_ids = [
            ingredient_data.get('id') for ingredient_data in valid_ingredients
        ]
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        ingredient_amounts = []
        for ingredient_data in valid_ingredients:
            ingredient = ingredients.get(id=ingredient_data.get('id'))
            ingredient_amounts.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data.get('amount')
                )
            )
        IngredientAmount.objects.bulk_create(ingredient_amounts)

    def create_tags(self, data, recipe):
        """Отправка на валидацию и создание тэгов у рецепта."""
        valid_tags = validate_tags(data.get('tags'))
        tags = Tag.objects.get_queryset().filter(id__in=valid_tags)
        recipe.tags.set(tags)

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта"""
        valid_ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(self.initial_data, recipe)
        self.create_ingredient_amount(valid_ingredients, recipe)
        return recipe

    def validate(self, data):
        """Валидация данных."""
        ingredients = self.initial_data.get('ingredients')
        valid_ingredients = validate_ingredients(ingredients)
        data['ingredients'] = valid_ingredients
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """Изменение рецепта"""
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        instance.tags.remove()
        self.create_tags(self.initial_data, instance)
        instance.ingredientamount_set.filter(recipe__in=[instance.id]).delete()
        valid_ingredients = validated_data.get(
            'ingredients', instance.ingredients)
        self.create_ingredient_amount(valid_ingredients, instance)
        return instance
