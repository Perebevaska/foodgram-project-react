from django.core.cache import cache
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (CartList, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.models import Subscription, User

from .validators import validate_ingredients, validate_tags


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, help_text='Введите e-mail')
    username = serializers.CharField(
        required=True, max_length=150, help_text='Введите nickname'
    )
    first_name = serializers.CharField(max_length=30, help_text='Введите имя.')
    last_name = serializers.CharField(
        max_length=30, help_text='Введите фамилию.'
    )
    password = serializers.CharField(required=True, write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password)
            user.save()

        return user

    def get_is_subscribed(self, obj):
        user_id = self.context.get('request').user.id
        return Subscription.objects.filter(
            author=obj.id, user=user_id
        ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        write_only_fields = ('password',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class ImageRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(
        read_only=True, many=True, source='ingredientamount_set'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def create(self, validated_data):
        valid_ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(self.initial_data, recipe)
        self.create_ingredient_amount(valid_ingredients, recipe)
        return recipe

    def create_ingredient_amount(self, valid_ingredients, recipe):
        for ingredient_data in valid_ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_data.get('id')
            )
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount'),
            )

    def create_tags(self, data, recipe):
        valid_tags = validate_tags(data.get('tags'))
        tags = Tag.objects.filter(id__in=valid_tags)
        recipe.tags.set(tags)

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return (
            user_id.is_authenticated
            and Favorite.objects.filter(user=user_id, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return (
            user_id.is_authenticated
            and CartList.objects.filter(user=user_id, recipe=obj).exists()
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients', [])
        valid_ingredients = validate_ingredients(ingredients)
        data['ingredients'] = valid_ingredients
        data['tags'] = data.get('tags', [])
        return data

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        if name is not None:
            instance.name = name
        if image is not None:
            instance.image = image
        if text is not None:
            instance.text = text
        if cooking_time is not None:
            instance.cooking_time = cooking_time
        instance.save()
        instance.tags.remove()
        self.create_tags(self.initial_data, instance)
        instance.ingredientamount_set.filter(recipe__in=[instance.id]).delete()
        valid_ingredients = validated_data.get(
            'ingredients', instance.ingredients
        )
        self.create_ingredient_amount(valid_ingredients, instance)
        return instance

    class Meta:
        model = Recipe
        fields = ('__all__')


class RecipeWithImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                author=obj.author, user=user
            ).exists()
        return False

    # def get_recipes(self, obj):
    #     limit = self.context.get('request').GET.get('recipes_limit')
    #     recipe_obj = obj.author.recipes.all()
    #     if limit:
    #         recipe_obj = recipe_obj[:int(limit)]
    #     prefetch = Prefetch('recipeingredient_set__ingredient')
    #     recipe_obj = recipe_obj.prefetch_related(prefetch)
    #     serializer = RecipeWithImageSerializer(recipe_obj, many=True)
    #     return serializer.data

    # пробую кеширование

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        cache_key = f"recipes_{obj.author.id}_{limit}"
        data = cache.get(cache_key)
        if data is None:
            prefetch = Prefetch('recipeingredient_set__ingredient')
            recipes = obj.author.recipes.all().prefetch_related(prefetch)
            if limit:
                limit = self.validate_integer(limit)
                recipes = recipes[:limit]
            serializer = RecipeWithImageSerializer(recipes, many=True)
            data = serializer.data
            cache.set(cache_key, data)
        return data

    def validate_integer(self, value):
        try:
            limit = int(value)
            if limit < 1:
                raise serializers.ValidationError(
                    'Количество рецептов должно быть больше 0'
                )
        except ValueError:
            raise serializers.ValidationError(
                'Число должно быть целым (integer).'
            )
        return limit


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
