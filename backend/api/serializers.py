from users.models import User, Subscription
from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe
from djoser.serializers import UserSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, help_text='Введите e-mail')
    username = serializers.CharField(
        required=True, max_length=150, help_text='Введите nickname')
    first_name = serializers.CharField(
        max_length=30, help_text='Введите имя.')
    last_name = serializers.CharField(
        max_length=30, help_text='Введите фамилию.')
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
            author=obj.id, user=user_id).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password', 'is_subscribed'
        )
        write_only_fields = ('password', )



class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами."""
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""
    class Meta:
        model = Recipe
        fields = '__all__'


#
# class RecipeSerializer(serializers.ModelSerializer):
#     author = CustomUserSerializer(read_only=True)
#     tags = TagsSerializer(read_only=True, many=True)
#     ingredients = IngredientSerializer(
#         read_only=True, many=True, source='ingredientamount_set')
#     image = Base64ImageField()
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#
#     def create(self, validated_data):
#         """Создание рецепта - writable nested serializers."""
#         valid_ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         recipe = Recipe.objects.create(**validated_data)
#         self.create_tags(self.initial_data, recipe)
#         self.create_ingredient_amount(valid_ingredients, recipe)
#         return recipe
#
#     def create_ingredient_amount(self, valid_ingredients, recipe):
#         """Создание уникальных записей: ингредиент - рецепт - количество."""
#         for ingredient_data in valid_ingredients:
#             ingredient = get_object_or_404(
#                 Ingredient, id=ingredient_data.get('id'))
#             IngredientAmount.objects.create(
#                 recipe=recipe,
#                 ingredient=ingredient,
#                 amount=ingredient_data.get('amount'))
#
#     def create_tags(self, data, recipe):
#         """Отправка на валидацию и создание тэгов у рецепта."""
#         valid_tags = validate_tags(data.get('tags'))
#         tags = Tag.objects.filter(id__in=valid_tags)
#         recipe.tags.set(tags)
#
#     def get_is_favorited(self, obj):
#         """Статус - рецепт в избранном или нет."""
#         user_id = self.context.get('request').user.id
#         return user_id.is_authenticated and Favorite.objects.filter(user=user_id, recipe=obj).exists()
#
#     def get_is_in_shopping_cart(self, obj):
#         """Статус - рецепт в избранном или нет."""
#         user_id = self.context.get('request').user.id
#         return user_id.is_authenticated and ShoppingCart.objects.filter(user=user_id, recipe=obj).exists()
#
#
#     def validate(self, data):
#         ingredients = self.initial_data.get('ingredients', [])
#         valid_ingredients = validate_ingredients(ingredients)
#         data['ingredients'] = valid_ingredients
#         data['tags'] = data.get('tags', [])
#         return data
#
#     def update(self, instance, validated_data):
#         """Обновление рецепта"""
#         name = validated_data.get('name')
#         image = validated_data.get('image')
#         text = validated_data.get('text')
#         cooking_time = validated_data.get('cooking_time')
#         if name is not None:
#             instance.name = name
#         if image is not None:
#             instance.image = image
#         if text is not None:
#             instance.text = text
#         if cooking_time is not None:
#             instance.cooking_time = cooking_time
#         instance.save()
#         instance.tags.remove()
#         self.create_tags(self.initial_data, instance)
#         instance.ingredientamount_set.filter(recipe__in=[instance.id]).delete()
#         valid_ingredients = validated_data.get('ingredients', instance.ingredients)
#         self.create_ingredient_amount(valid_ingredients, instance)
#         return instance
#
#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'tags', 'author', 'ingredients', 'is_favorited',
#             'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
#         )